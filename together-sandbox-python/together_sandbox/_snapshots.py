from __future__ import annotations


import os
import platform
import re
import httpx

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4
from .api.client import AuthenticatedClient as ApiClient
from ._utils import _base32_encode, _strip_ansi
from ._configuration import is_local_environment, get_inferred_registry_url

# ── Snapshot API endpoint functions ──────────────────────────────────────────
from .api.api.default.create_snapshot import asyncio as create_snapshot_api
from .api.api.default.alias_snapshot import asyncio as alias_snapshot_api
from .api.api.default.get_snapshot_by_alias import asyncio as get_snapshot_by_alias_api

# ── Snapshot API models ───────────────────────────────────────────────────────
from .api.models.alias_snapshot_body import AliasSnapshotBody
from .api.models.create_snapshot_body import CreateSnapshotBody
from .api.models.create_snapshot_body_image import CreateSnapshotBodyImage
from .api.models.create_snapshot_body_image_architecture import CreateSnapshotBodyImageArchitecture
from .api.models.snapshot import Snapshot
from .api.types import UNSET

# ── Docker helpers ────────────────────────────────────────────────────────────
from .docker import (
    DockerBuildOptions,
    DockerLoginOptions,
    build_docker_image,
    docker_login,
    is_docker_available,
    push_docker_image,
)


# ─── Snapshot types ──────────────────────────────────────────────────────────


@dataclass
class SnapshotProgress:
    step: str
    output: str


@dataclass
class CreateSnapshotResult:
    snapshot_id: str
    alias: str | None = None


@dataclass
class CreateFromContextParams:
    context: str
    dockerfile: str | None = None
    alias: str | None = None
    on_progress: Callable[[SnapshotProgress], None] | None = None
    memory_snapshot: bool | None = None


@dataclass
class CreateFromImageParams:
    image: str
    alias: str | None = None
    on_progress: Callable[[SnapshotProgress], None] | None = None


CreateSnapshotParams = CreateFromContextParams | CreateFromImageParams

# ─── Snapshot helpers ─────────────────────────────────────────────────────────


def _parse_alias(default_namespace: str, alias: str) -> tuple[str, str]:
    parts = alias.split("@")
    if len(parts) > 2:
        raise ValueError(f'Alias "{alias}" is invalid, must be in the format of name@tag')
    namespace = parts[0] if len(parts) == 2 else default_namespace
    tag = parts[1] if len(parts) == 2 else alias
    if len(namespace) > 64 or len(tag) > 64:
        raise ValueError(
            f'Namespace "{namespace}" or tag "{tag}" exceeds 64 characters'
        )
    if not re.match(r"^[a-zA-Z0-9\-_]+$", namespace) or not re.match(r"^[a-zA-Z0-9\-_]+$", tag):
        raise ValueError(
            f'Namespace "{namespace}" or tag "{tag}" must only contain letters, digits, dashes and underscores'
        )
    return namespace, tag


@dataclass
class ImageReference:
    """Parsed Docker image reference components."""
    name: str
    registry: str | None = None
    repository: str | None = None
    tag: str | None = None


def _parse_image_reference(image: str) -> ImageReference:
    """
    Parse a Docker image reference into its components.

    Handles formats like:
    - ubuntu
    - node:24
    - org/myapp
    - org/myapp:latest
    - ghcr.io/org/node:24
    - registry.example.com:5000/org/app:v1

    A registry is present if the first path segment contains '.' or ':',
    indicating a registry hostname.
    """
    # Find the last colon and check if the text after it contains a slash
    last_colon = image.rfind(":")
    if last_colon != -1:
        after_colon = image[last_colon + 1:]
        if "/" not in after_colon:
            tag = after_colon
            image_without_tag = image[:last_colon]
        else:
            image_without_tag = image
            tag = None
    else:
        image_without_tag = image
        tag = None

    # Split the image part by "/"
    parts = image_without_tag.split("/")

    if len(parts) == 1:
        # Just "name" or "name:tag"
        return ImageReference(name=parts[0], tag=tag if tag else None)

    if len(parts) == 2:
        # Either "registry/name" or "repo/name"
        first_part = parts[0]
        second_part = parts[1]
        if "." in first_part or ":" in first_part:
            # It's a registry
            return ImageReference(registry=first_part, name=second_part, tag=tag if tag else None)
        else:
            # It's a repository
            return ImageReference(repository=first_part, name=second_part, tag=tag if tag else None)

    if len(parts) >= 3:
        # "registry/repo/name" or more
        first_part = parts[0]
        if "." in first_part or ":" in first_part:
            # First part is a registry
            registry = first_part
            repository = parts[1]
            name = parts[2]
            return ImageReference(registry=registry, repository=repository, name=name, tag=tag if tag else None)
        else:
            # No registry, treat first two parts as namespace/repo hierarchy
            # (unlikely but handle it as repo/name)
            repository = parts[0]
            name = parts[1]
            return ImageReference(repository=repository, name=name, tag=tag if tag else None)

    # Fallback (should not reach here)
    return ImageReference(name=image_without_tag)


async def _get_meta_info(api_key: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.codesandbox.stream/meta/info",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        response.raise_for_status()
        return response.json()


# ─── SnapshotsNamespace ───────────────────────────────────────────────────────


class SnapshotsNamespace:
    """
    Snapshot build and management operations, accessed as ``sdk.snapshots.*``.
    """

    def __init__(
        self,
        api_client: ApiClient,
        api_key: str,
        base_url: str,
    ) -> None:
        self._api_client = api_client
        self._api_key = api_key
        self._base_url = base_url

    # ─── Public entry points ──────────────────────────────────────────────────

    async def create(self, params: CreateSnapshotParams) -> CreateSnapshotResult:
        """Create a snapshot from either a Docker context or a public Docker image."""
        if isinstance(params, CreateFromContextParams):
            # Context-based snapshot — requires Docker
            if not await is_docker_available():
                raise RuntimeError(
                    "Docker is not available. Please install Docker to use snapshot builds."
                )

            return await self._build_and_register(params)
        else:
            # Image-based snapshot — no Docker required
            ref = _parse_image_reference(params.image)

            def _emit(step: str, output: str) -> None:
                if params.on_progress:
                    params.on_progress(SnapshotProgress(step=step, output=output))

            _emit("register", "Creating snapshot from image...")
            snapshot_data = await create_snapshot_api(
                client=self._api_client,
                body=CreateSnapshotBody(
                    image=CreateSnapshotBodyImage(
                        registry=ref.registry or UNSET,
                        repository=ref.repository or UNSET,
                        name=ref.name,
                        tag=ref.tag or UNSET,
                        architecture=CreateSnapshotBodyImageArchitecture("amd64"),
                    )
                ),
            )

            if snapshot_data is None or not hasattr(snapshot_data, "id"):
                raise RuntimeError("Snapshot creation returned no data")

            snapshot_id = str(snapshot_data.id)
            alias: str | None = None

            if params.alias:
                _emit("alias", "Creating alias...")
                namespace, alias_tag = _parse_alias(ref.name, params.alias)
                alias = f"{namespace}@{alias_tag}"
                await alias_snapshot_api(
                    snapshot_data.id,
                    client=self._api_client,
                    body=AliasSnapshotBody(alias=alias),
                )

            return CreateSnapshotResult(snapshot_id=snapshot_id, alias=alias)

    async def get_snapshot(self, alias: str) -> Snapshot:
        """
        Get snapshot information by alias.

        Args:
            alias: Snapshot alias (format: "namespace@alias" or just "alias")

        Returns:
            Snapshot: Snapshot model with id, type, byte_size, and metadata

        Raises:
            RuntimeError: If the snapshot is not found or API returns no data
            errors.UnexpectedStatus: If the API request fails

        Example:
            >>> snapshot = await sdk.snapshots.get_snapshot("my-app@latest")
            >>> print(snapshot.id)
            >>> print(snapshot.byte_size)
        """
        # Remove leading '@' if present (for consistency with API)
        clean_alias = alias.lstrip("@")

        snapshot_data = await get_snapshot_by_alias_api(
            clean_alias,
            client=self._api_client,
        )

        if snapshot_data is None:
            raise RuntimeError(f"Snapshot with alias '{alias}' not found")

        return snapshot_data

    # ─── Private helpers ──────────────────────────────────────────────────────

    async def _build_and_register(
        self,
        params: CreateFromContextParams,
    ) -> CreateSnapshotResult:
        architecture = (
            "arm64"
            if platform.machine().lower() == "arm64" and is_local_environment(self._base_url)
            else "amd64"
        )
        context = os.path.realpath(params.context)
        dockerfile_path = (
            os.path.realpath(params.dockerfile) if params.dockerfile else None
        )
        alias_default_namespace = os.path.basename(context)

        meta_info = await _get_meta_info(self._api_key)
        team_id = meta_info.get("auth", {}).get("team")
        if not team_id:
            raise RuntimeError(
                "Failed to fetch team information for the provided API key. "
                "Please ensure your TOGETHER_API_KEY is correct and has access to a team."
            )

        repository = _base32_encode(team_id)
        registry = get_inferred_registry_url(self._base_url)
        image_name = f"image-{uuid4()}".lower()
        image_tag = str(uuid4()).lower()
        full_image_name = f"{registry}/{repository}/{image_name}:{image_tag}"

        def _emit(step: str, output: str) -> None:
            if params.on_progress:
                params.on_progress(SnapshotProgress(step=step, output=output))

        _emit("prepare", "Preparing snapshot...")
        _emit("build", "Building snapshot...")
        await build_docker_image(
            DockerBuildOptions(
                dockerfile_path=dockerfile_path,
                image_name=full_image_name,
                context=context,
                architecture=architecture,
                on_output=lambda out: _emit("build", _strip_ansi(out)),
            )
        )

        _emit("auth", "Authenticating...")
        await docker_login(
            DockerLoginOptions(
                registry=registry,
                username="_token",
                password=self._api_key,
                on_output=lambda out: _emit("auth", _strip_ansi(out)),
            )
        )

        _emit("push", "Pushing Docker image...")
        await push_docker_image(
            full_image_name,
            on_output=lambda out: _emit("push", _strip_ansi(out)),
        )

        _emit("register", "Registering snapshot...")
        snapshot_data = await create_snapshot_api(
            client=self._api_client,
            body=CreateSnapshotBody(
                image=CreateSnapshotBodyImage(
                    registry=registry,
                    repository=repository,
                    name=image_name,
                    tag=image_tag,
                    architecture=CreateSnapshotBodyImageArchitecture(architecture),
                )
            ),
        )

        if snapshot_data is None or not hasattr(snapshot_data, "id"):
            raise RuntimeError("Snapshot creation returned no data")

        snapshot_id = str(snapshot_data.id)
        alias: str | None = None

        if params.alias:
            _emit("alias", "Creating alias...")
            namespace, alias_tag = _parse_alias(alias_default_namespace, params.alias)
            alias = f"{namespace}@{alias_tag}"
            await alias_snapshot_api(
                snapshot_data.id,
                client=self._api_client,
                body=AliasSnapshotBody(alias=alias),
            )

        return CreateSnapshotResult(snapshot_id=snapshot_id, alias=alias)

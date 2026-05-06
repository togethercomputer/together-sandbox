from __future__ import annotations


import os
import platform

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4, UUID
from .api.client import AuthenticatedClient as ApiClient
from ._utils import _strip_ansi, RetryConfig, _call_api
from ._configuration import is_local_environment

# ── Snapshot API endpoint functions (detailed variants) ───────────────────────
from .api.api.default.create_snapshot import asyncio_detailed as create_snapshot_api
from .api.api.default.alias_snapshot import asyncio_detailed as alias_snapshot_api
from .api.api.default.get_snapshot_by_alias import (
    asyncio_detailed as get_snapshot_by_alias_api,
)
from .api.api.default.issue_container_registry_credential import (
    asyncio_detailed as issue_container_registry_credential_api,
)
from .api.api.default.get_snapshot import asyncio_detailed as get_snapshot_api
from .api.api.default.list_snapshots import asyncio_detailed as list_snapshots_api
from .api.api.default.delete_snapshot import asyncio_detailed as delete_snapshot_api
from .api.api.default.delete_snapshot_by_alias import (
    asyncio_detailed as delete_snapshot_by_alias_api,
)

# ── Snapshot API models ───────────────────────────────────────────────────────
from .api.models.alias_snapshot_body import AliasSnapshotBody
from .api.models.create_snapshot_body import CreateSnapshotBody
from .api.models.create_snapshot_body_architecture import CreateSnapshotBodyArchitecture
from .api.models.container_registry_credential import ContainerRegistryCredential
from .api.models.snapshot import Snapshot
from .api.models.error import Error
from .api.types import UNSET

# ── Helpers ────────────────────────────────────────────────────────────
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
class CreateContextSnapshotParams:
    context: str
    dockerfile: str | None = None
    alias: str | None = None
    on_progress: Callable[[SnapshotProgress], None] | None = None
    memory_snapshot: bool | None = None


@dataclass
class CreateImageSnapshotParams:
    image: str
    alias: str | None = None
    on_progress: Callable[[SnapshotProgress], None] | None = None


CreateSnapshotParams = CreateContextSnapshotParams | CreateImageSnapshotParams

# ─── SnapshotsNamespace ───────────────────────────────────────────────────────


class SnapshotsNamespace:
    """
    Snapshot build and management operations, accessed as ``sdk.snapshots.*``.
    """

    def __init__(
        self,
        api_client: ApiClient,
        base_url: str,
        *,
        retry: RetryConfig | None = None,
    ) -> None:
        self._api_client = api_client
        self._base_url = base_url
        self._retry = retry

    # ─── Public entry points ──────────────────────────────────────────────────

    async def alias(self, snapshot_id: str, alias: str) -> None:
        """Create an alias for an existing snapshot"""
        await _call_api(
            "snapshots.alias",
            lambda: alias_snapshot_api(
                UUID(snapshot_id),
                client=self._api_client,
                body=AliasSnapshotBody(alias=alias),
            ),
            self._retry,
            context=f"for snapshot {snapshot_id!r}",
        )

    async def create(self, params: CreateSnapshotParams) -> CreateSnapshotResult:
        """Create a snapshot from either a Docker context or a public Docker image.

        .. note::
            The ``snapshots.create`` operation is not idempotent: retrying on a
            transient 500 error after the snapshot was already created will
            register a duplicate. If you use :class:`RetryConfig`, consider
            excluding this operation::

                RetryConfig(should_retry=lambda ctx: ctx.operation != "snapshots.create")
        """
        if isinstance(params, CreateContextSnapshotParams):
            # Context-based snapshot — requires Docker
            if not await is_docker_available():
                raise RuntimeError(
                    "Docker is not available. Please install Docker to use snapshot builds."
                )

            return await self._build_and_register(params)
        else:
            # Image-based snapshot — no Docker required
            def _emit(step: str, output: str) -> None:
                if params.on_progress:
                    params.on_progress(SnapshotProgress(step=step, output=output))

            _emit("register", "Creating snapshot from image...")
            snapshot_data = await _call_api(
                "snapshots.create",
                lambda: create_snapshot_api(
                    client=self._api_client,
                    body=CreateSnapshotBody(
                        image=params.image,
                        architecture=CreateSnapshotBodyArchitecture.AMD64,
                    ),
                ),
                self._retry,
            )

            snapshot_id = str(snapshot_data.id)

            if params.alias:
                alias = params.alias
                _emit("alias", "Creating alias...")
                await _call_api(
                    "snapshots.alias",
                    lambda: alias_snapshot_api(
                        snapshot_data.id,
                        client=self._api_client,
                        body=AliasSnapshotBody(alias=alias),
                    ),
                    self._retry,
                )

            return CreateSnapshotResult(snapshot_id=snapshot_id, alias=params.alias)

    async def get_by_id(self, id: str) -> Snapshot:
        """
        Get snapshot information by id.

        Args:
            id: Snapshot id

        Returns:
            Snapshot: Snapshot model with id, type, byte_size, and metadata

        Raises:
            RuntimeError: If the snapshot is not found or the API returns an
                application-level error response.
            httpx.TimeoutException: If the request to the snapshot API times out.

        Example:
            >>> snapshot = await sdk.snapshots.get("some-id")
            >>> print(snapshot.id)
            >>> print(snapshot.byte_size)
        """
        return await _call_api(
            "snapshots.getById",
            lambda: get_snapshot_api(UUID(id), client=self._api_client),
            self._retry,
            context=f"for id {id!r}",
        )

    async def get_by_alias(self, alias: str) -> Snapshot:
        """
        Get snapshot information by alias.

        Args:
            alias: Snapshot alias

        Returns:
            Snapshot: Snapshot model with id, type, byte_size, and metadata

        Raises:
            RuntimeError: If the snapshot is not found or API returns no data
            httpx.TimeoutException: If the API request fails

        Example:
            >>> snapshot = await sdk.snapshots.get_by_alias("my-app@latest")
            >>> print(snapshot.id)
            >>> print(snapshot.byte_size)
        """
        # Remove leading '@' if present (for consistency with API)
        clean_alias = alias.lstrip("@")

        return await _call_api(
            "snapshots.getByAlias",
            lambda: get_snapshot_by_alias_api(
                clean_alias,
                client=self._api_client,
            ),
            self._retry,
            context=f"for alias {alias!r}",
        )

    async def list(self) -> list[Snapshot]:
        """
        List snapshots.

        Returns:
            list[Snapshot]: List of snapshot models with id, type, byte_size, and metadata

        Raises:
            RuntimeError: If the API returns no data
            httpx.TimeoutException: If the API request fails

        Example:
            >>> snapshots = await sdk.snapshots.list()
            >>> for snapshot in snapshots:
            ...     print(snapshot.id)
        """
        return await _call_api(
            "snapshots.list",
            lambda: list_snapshots_api(client=self._api_client),
            self._retry,
        )

    async def delete_by_id(self, id: str) -> None:
        """
        Delete a snapshot by id.

        Args:
            id: Snapshot id

        Raises:
            RuntimeError: If the API request fails
        """
        await _call_api(
            "snapshots.deleteById",
            lambda: delete_snapshot_api(UUID(id), client=self._api_client),
            self._retry,
            context=f"for snapshot {id!r}",
        )

    async def delete_by_alias(self, alias: str) -> None:
        """
        Delete a snapshot by alias.

        Args:
            alias: Snapshot alias

        Raises:
            RuntimeError: If the API request fails
        """
        # Remove leading '@' if present (for consistency with API)
        clean_alias = alias.lstrip("@")

        await _call_api(
            "snapshots.deleteByAlias",
            lambda: delete_snapshot_by_alias_api(
                clean_alias,
                client=self._api_client,
            ),
            self._retry,
            context=f"for snapshot {alias!r}",
        )

    # ─── Private helpers ──────────────────────────────────────────────────────

    async def _build_and_register(
        self,
        params: CreateContextSnapshotParams,
    ) -> CreateSnapshotResult:
        architecture = (
            CreateSnapshotBodyArchitecture.ARM64
            if platform.machine().lower() == "arm64"
            and is_local_environment(self._base_url)
            else CreateSnapshotBodyArchitecture.AMD64
        )
        context = os.path.realpath(params.context)
        dockerfile_path = (
            os.path.realpath(params.dockerfile) if params.dockerfile else None
        )

        credential: ContainerRegistryCredential = await _call_api(
            "snapshots.issueContainerRegistryCredential",
            lambda: issue_container_registry_credential_api(client=self._api_client),
            self._retry,
        )
        registry_url = credential.registry_url
        registry_host = registry_url.split("/")[0]
        image_name = f"image-{uuid4()}".lower()
        image_tag = str(uuid4()).lower()
        full_image_name = f"{registry_url}/{image_name}:{image_tag}"

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
                registry=registry_host,
                username=credential.username,
                password=credential.password,
                on_output=lambda out: _emit("auth", _strip_ansi(out)),
            )
        )

        _emit("push", "Pushing Docker image...")
        await push_docker_image(
            full_image_name,
            on_output=lambda out: _emit("push", _strip_ansi(out)),
        )

        _emit("register", "Registering snapshot...")
        snapshot_data = await _call_api(
            "snapshots.create",
            lambda: create_snapshot_api(
                client=self._api_client,
                body=CreateSnapshotBody(
                    image=full_image_name,
                    architecture=architecture,
                ),
            ),
            self._retry,
        )

        snapshot_id = str(snapshot_data.id)

        if params.alias:
            alias = params.alias
            _emit("alias", "Creating alias...")
            await _call_api(
                "snapshots.alias",
                lambda: alias_snapshot_api(
                    snapshot_data.id,
                    client=self._api_client,
                    body=AliasSnapshotBody(alias=alias),
                ),
                self._retry,
            )

        return CreateSnapshotResult(snapshot_id=snapshot_id, alias=params.alias)

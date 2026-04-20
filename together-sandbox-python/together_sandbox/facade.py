"""
Unified Together Sandbox client.

This module provides :class:`TogetherSandbox` — a thin facade over the two
generated SDK clients that handles the vmStart → SandboxClient handoff
transparently.

Usage::

    import asyncio
    from together_sandbox import TogetherSandbox

    async def main():
        sdk = TogetherSandbox(api_key="your-api-key")
        async with await sdk.sandboxes.start("sandbox-id") as sandbox:
            content = await sandbox.files.read_file("/package.json")
            print(content)

    asyncio.run(main())
"""

from __future__ import annotations

import base64
import os
import platform
import re
from collections.abc import Callable
from dataclasses import dataclass
from types import TracebackType
from typing import Any, AsyncIterator, List
from urllib.parse import urlparse
from uuid import uuid4

import httpx

# ── Management API client ─────────────────────────────────────────────────────
from .api.client import AuthenticatedClient as ApiClient

# ── Management API endpoint functions ─────────────────────────────────────────
from .api.api.default.start_sandbox import asyncio as start_sandbox_api
from .api.api.default.stop_sandbox import asyncio as stop_sandbox_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.sandbox import Sandbox as SandboxModel
from .api.models.stop_sandbox_body import StopSandboxBody
from .api.models.stop_sandbox_body_stop_type import StopSandboxBodyStopType

# ── Sandbox API client ────────────────────────────────────────────────────────
from .sandbox.client import AuthenticatedClient as SandboxClient

# ── Sandbox API endpoint functions (non-SSE) ─────────────────────────────────
from .sandbox.api.files.read_file import asyncio as read_file_api
from .sandbox.api.files.create_file import asyncio as create_file_api
from .sandbox.api.files.delete_file import asyncio as delete_file_api
from .sandbox.api.files.get_file_stat import asyncio as get_file_stat_api
from .sandbox.api.files.perform_file_action import asyncio as perform_file_action_api
from .sandbox.api.execs.list_execs import asyncio as list_execs_api
from .sandbox.api.execs.create_exec import asyncio as create_exec_api
from .sandbox.api.execs.get_exec import asyncio as get_exec_api
from .sandbox.api.execs.get_exec_output import asyncio as get_exec_output_api
from .sandbox.api.execs.update_exec import asyncio as update_exec_api
from .sandbox.api.execs.delete_exec import asyncio as delete_exec_api
from .sandbox.api.execs.exec_exec_stdin import asyncio as exec_exec_stdin_api
from .sandbox.api.ports.list_ports import asyncio as list_ports_api
from .sandbox.api.directories.list_directory import asyncio as list_directory_api
from .sandbox.api.directories.create_directory import asyncio as create_directory_api
from .sandbox.api.directories.delete_directory import asyncio as delete_directory_api
from .sandbox.api.tasks.list_tasks import asyncio as list_tasks_api
from .sandbox.api.tasks.list_setup_tasks import asyncio as list_setup_tasks_api
from .sandbox.api.tasks.get_task import asyncio as get_task_api
from .sandbox.api.tasks.execute_task_action import asyncio as execute_task_action_api

# ── Sandbox API models ────────────────────────────────────────────────────────
from .sandbox.models.create_exec_request import CreateExecRequest
from .sandbox.models.file_action_request import FileActionRequest
from .sandbox.models.file_action_request_action import FileActionRequestAction
from .sandbox.models.file_action_response import FileActionResponse
from .sandbox.models.file_info import FileInfo
from .sandbox.models.file_operation_response import FileOperationResponse
from .sandbox.models.file_read_response import FileReadResponse
from .sandbox.models.exec_stdin import ExecStdin
from .sandbox.models.task_action_type import TaskActionType
from .sandbox.models.update_exec_request import UpdateExecRequest
from .sandbox.types import File

# ── SSE streaming helper ─────────────────────────────────────────────────────
from ._streaming import stream_sse_json

# ── Snapshot API endpoint functions ──────────────────────────────────────────
from .api.api.default.create_snapshot import asyncio as create_snapshot_api
from .api.api.default.alias_snapshot import asyncio as alias_snapshot_api

# ── Snapshot API models ───────────────────────────────────────────────────────
from .api.models.alias_snapshot_body import AliasSnapshotBody
from .api.models.create_snapshot_body import CreateSnapshotBody
from .api.models.create_snapshot_body_image import CreateSnapshotBodyImage
from .api.models.create_snapshot_body_image_architecture import CreateSnapshotBodyImageArchitecture
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


# ─── Internal helpers ─────────────────────────────────────────────────────────


def _resolve_connection(sandbox: SandboxModel) -> tuple[str, str]:
    """
    Extract the agent connection details from the Sandbox model.
    """
    if not sandbox.agent_url or not sandbox.agent_token:
        raise RuntimeError("Sandbox has no agent connection details")
    return sandbox.agent_url, sandbox.agent_token


# ─── Files facade ─────────────────────────────────────────────────────────────


class Files:
    """
    File operations facade that wraps the low-level files client.

    Adds ``move_file``, ``copy_file``, and ``watch`` methods while
    delegating existing methods to the underlying client.
    """

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def read(self, path: str) -> str:
        """Read file content at the specified path."""
        result = await read_file_api(path, client=self._client)
        return result.content

    async def create(
        self, path: str, content: bytes | str
    ) -> str:
        """
        Create a file at the specified path with binary content.

        Args:
            path: File path to create
            content: File content as bytes or string (will be encoded as UTF-8)

        Returns:
            The created file content
        """
        import io

        # Convert string to bytes if necessary
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content

        # Create a File object with binary content
        file_obj = File(payload=io.BytesIO(content_bytes))

        result = await create_file_api(path, client=self._client, body=file_obj)
        return result.content

    async def delete(self, path: str) -> None:
        """Delete a file at the specified path."""
        await delete_file_api(path, client=self._client)

    async def move(self, from_path: str, to_path: str) -> None:
        """Move a file from one path to another."""
        await perform_file_action_api(
            from_path,
            client=self._client,
            body=FileActionRequest(
                action=FileActionRequestAction.MOVE,
                destination=to_path,
            ),
        )

    async def copy(self, from_path: str, to_path: str) -> None:
        """Copy a file from one path to another."""
        await perform_file_action_api(
            from_path,
            client=self._client,
            body=FileActionRequest(
                action=FileActionRequestAction.COPY,
                destination=to_path,
            ),
        )

    async def stat(self, path: str) -> FileInfo:
        """Get file metadata at the specified path."""
        return await get_file_stat_api(path, client=self._client)

    def watch(
        self,
        path: str,
        recursive: bool | None = None,
        ignore_patterns: List[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Watch a directory for file system changes via SSE.

        Renamed from ``create_watcher`` for consistency.
        """
        params: dict[str, Any] = {}
        if recursive is not None:
            params["recursive"] = recursive
        if ignore_patterns is not None:
            params["ignorePatterns"] = ignore_patterns
        return stream_sse_json(
            self._client.get_async_httpx_client(),
            f"/api/v1/stream/directories/watcher/{path}",
            params=params,
        )


# ─── Execs facade ─────────────────────────────────────────────────────────────


class Execs:
    """
    Exec operations facade with renamed SSE methods.

    - ``get_exec_output`` → ``stream_output``
    - ``exec_exec_stdin`` → ``send_stdin``
    - ``stream_execs_list`` → ``stream_list``
    - ``connect_to_exec_web_socket`` → removed
    """

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list(self):
        """List all active execs."""
        result = await list_execs_api(client=self._client)
        return result.execs

    async def create(self, body: CreateExecRequest):
        """Create a new exec."""
        result = await create_exec_api(client=self._client, body=body)
        if result is None:
            raise RuntimeError("createExec returned None")
        return result

    async def get(self, id_: str):
        """Get exec by ID."""
        result = await get_exec_api(id_, client=self._client)
        assert result is not None
        return result

    async def update(self, id_: str, body: UpdateExecRequest):
        """Update exec status."""
        result = await update_exec_api(id_, client=self._client, body=body)
        if result is None:
            raise RuntimeError(f"updateExec returned None for id {id_!r}")
        return result

    async def delete(self, id_: str) -> None:
        """Delete an exec."""
        await delete_exec_api(id_, client=self._client)

    def stream_output(
        self, id_: str, last_sequence: int | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream exec output via SSE (renamed from get_exec_output)."""
        params: dict[str, Any] = {}
        if last_sequence is not None:
            params["lastSequence"] = last_sequence
        return stream_sse_json(
            self._client.get_async_httpx_client(),
            f"/api/v1/stream/execs/{id_}/io",
            params=params,
        )

    async def get_output(
        self, id_: str, last_sequence: int | None = None
    ) -> str:
        """Fetch exec output as plain text (one-shot poll)."""
        result = await get_exec_output_api(id_, client=self._client, last_sequence=last_sequence)
        if isinstance(result, str):
            return result
        if result and hasattr(result, 'output'):
            return result.output
        return ""

    async def send_stdin(self, id_: str, body: ExecStdin):
        """Send stdin to an exec (renamed from exec_exec_stdin)."""
        result = await exec_exec_stdin_api(id_, client=self._client, body=body)
        assert result is not None
        return result

    def stream_list(self) -> AsyncIterator[dict[str, Any]]:
        """Stream list of all active execs via SSE (renamed from stream_execs_list)."""
        return stream_sse_json(
            self._client.get_async_httpx_client(),
            "/api/v1/stream/execs",
        )


# ─── Ports facade ─────────────────────────────────────────────────────────────


class Ports:
    """
    Port operations facade with renamed SSE method.

    - ``stream_ports_list`` → ``stream_list``
    """

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list(self):
        """List open ports."""
        result = await list_ports_api(client=self._client)
        return result.ports

    def stream_list(self) -> AsyncIterator[dict[str, Any]]:
        """Stream port changes via SSE (renamed from stream_ports_list)."""
        return stream_sse_json(
            self._client.get_async_httpx_client(),
            "/api/v1/stream/ports",
        )


# ─── Directories facade ──────────────────────────────────────────────────────


class Directories:
    """Directory operations (list, create, delete)."""

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list(self, path: str) -> List[FileInfo]:
        """List directory contents."""
        result = await list_directory_api(path, client=self._client)
        return result.files

    async def create(self, path: str) -> None:
        """Create a directory."""
        await create_directory_api(path, client=self._client)

    async def delete(self, path: str) -> None:
        """Delete a directory."""
        await delete_directory_api(path, client=self._client)


# ─── Tasks facade ─────────────────────────────────────────────────────────────


class Tasks:
    """Task operations (list, list_setup, get, action)."""

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list(self):
        """List all tasks."""
        result = await list_tasks_api(client=self._client)
        return result.tasks

    async def list_setup(self):
        """List setup tasks."""
        result = await list_setup_tasks_api(client=self._client)
        return result.setup_tasks

    async def get(self, id_: str):
        """Get task by ID."""
        result = await get_task_api(id_, client=self._client)
        return result.task

    async def action(self, id_: str, action_type: TaskActionType):
        """Execute an action on a task."""
        return await execute_task_action_api(id_, client=self._client, action_type=action_type)


# ─── Sandbox (connected sandbox) ─────────────────────────────────────────────


class Sandbox:
    """
    A running VM with a fully-initialized sandbox client attached.

    Access sandbox operations through the sub-namespaces::

        await sandbox.files.read_file("/path")
        await sandbox.files.move_file("/src", "/dest")
        await sandbox.files.copy_file("/src", "/dest")
        await sandbox.execs.create_exec(CreateExecRequest(...))
        await sandbox.execs.send_stdin(id_, body)
        async for event in sandbox.execs.stream_output(id_):
            ...
        await sandbox.tasks.list_tasks()
        await sandbox.ports.list_ports()

    Lifecycle methods call back to the management API::

        await sandbox.shutdown()
        await sandbox.hibernate()

    Can be used as an async context manager::

        async with await sdk.sandboxes.start(id) as sandbox:
            await sandbox.files.read_file("/path")
        # Closes the sandbox HTTP connection on exit.
        # Does NOT automatically shut down the VM — call shutdown() explicitly.
    """

    def __init__(
        self,
        vm_info: SandboxModel,
        sandbox_client: SandboxClient,
        api_client: ApiClient,
    ) -> None:
        self._vm_info = vm_info
        self._sandbox_client = sandbox_client
        self._api_client = api_client

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        """The VM/sandbox ID."""
        if not self._vm_info.id:
            raise RuntimeError("Sandbox has no ID")
        return self._vm_info.id

    @property
    def vm_info(self) -> SandboxModel:
        """Raw sandbox model (id, agent_url, agent_token, etc.)."""
        return self._vm_info

    # ── Sandbox sub-namespace delegation ──────────────────────────────────────

    @property
    def files(self) -> Files:
        """File system operations (read, create, delete, move, copy, stat, watch)."""
        return Files(self._sandbox_client)

    @property
    def directories(self) -> Directories:
        """Directory operations (list, create, delete)."""
        return Directories(self._sandbox_client)

    @property
    def execs(self) -> Execs:
        """Shell exec operations (create, get, update, stream_output, send_stdin, stream_list)."""
        return Execs(self._sandbox_client)

    @property
    def tasks(self) -> Tasks:
        """Task operations (list, list_setup, get, action)."""
        return Tasks(self._sandbox_client)

    @property
    def ports(self) -> Ports:
        """Port discovery (list, stream_list)."""
        return Ports(self._sandbox_client)

    # NOTE: sandbox.streams is removed — use sandbox.files.watch() instead

    # ── Lifecycle methods ─────────────────────────────────────────────────────

    async def hibernate(self) -> None:
        """Suspend (hibernate) this VM."""
        await stop_sandbox_api(self.id, client=self._api_client,
                               body=StopSandboxBody(stop_type=StopSandboxBodyStopType.HIBERNATE))

    async def shutdown(self) -> None:
        """Shut down this VM."""
        await stop_sandbox_api(self.id, client=self._api_client,
                               body=StopSandboxBody(stop_type=StopSandboxBodyStopType.SHUTDOWN))

    async def close(self) -> None:
        """Close the underlying sandbox client connection."""
        await self._sandbox_client.get_async_httpx_client().aclose()

    # ── Async context manager ─────────────────────────────────────────────────

    async def __aenter__(self) -> "Sandbox":
        await self._sandbox_client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._sandbox_client.__aexit__(exc_type, exc_val, exc_tb)

    # ── Static factory methods ──────────────────────────────────────────────

    @classmethod
    async def start(
        cls,
        sandbox_id: str,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.codesandbox.io",
        start_options: dict | None = None,
    ) -> "Sandbox":
        """
        Start a sandbox in a single call (classmethod factory).

        Example::

            sandbox = await Sandbox.start("sandbox-id", api_key="your-key")
        """
        sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        return await sdk.sandboxes.start(sandbox_id, start_options=start_options)

    @classmethod
    async def hibernate(
        cls,
        sandbox_id: str,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.codesandbox.io",
    ) -> None:
        """Hibernate a sandbox by ID without a running Sandbox instance."""
        sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        await sdk.sandboxes.hibernate(sandbox_id)

    @classmethod
    async def shutdown(
        cls,
        sandbox_id: str,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.codesandbox.io",
    ) -> None:
        """Shut down a sandbox by ID without a running Sandbox instance."""
        sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        await sdk.sandboxes.shutdown(sandbox_id)

# ─── SandboxesNamespace ───────────────────────────────────────────────────────


class SandboxesNamespace:
    """
    Sandbox lifecycle operations accessed as ``sdk.sandboxes.*``.
    """

    def __init__(self, api_client: ApiClient) -> None:
        self._api_client = api_client

    async def start(
        self,
        sandbox_id: str,
        *,
        start_options: dict | None = None,
    ) -> Sandbox:
        """
        Start the VM for the given sandbox and return a :class:`Sandbox`
        with a fully wired sandbox client.

        Args:
            sandbox_id: The sandbox (VM) ID to start.
            start_options: Optional start options (e.g., version_number).

        Returns:
            A ready-to-use :class:`Sandbox` with all sub-namespaces.
        """
        response = await start_sandbox_api(sandbox_id, client=self._api_client, body=start_options)
        vm_info = response.data

        if vm_info is None:
            raise RuntimeError(
                f"startSandbox for sandbox '{sandbox_id}' returned no data. "
                "Check that the sandbox ID is valid and your API key has the required scopes."
            )

        url, token = _resolve_connection(vm_info)

        sandbox_client = SandboxClient(
            base_url=url,
            token=token,
            prefix="Bearer",
            raise_on_unexpected_status=True,
        )

        return Sandbox(vm_info, sandbox_client, self._api_client)

    async def hibernate(self, sandbox_id: str) -> None:
        """Hibernate (suspend) a VM by sandbox ID."""
        await stop_sandbox_api(sandbox_id, client=self._api_client,
                               body=StopSandboxBody(stop_type=StopSandboxBodyStopType.HIBERNATE))

    async def shutdown(self, sandbox_id: str) -> None:
        """Shut down a VM by sandbox ID."""
        await stop_sandbox_api(sandbox_id, client=self._api_client,
                               body=StopSandboxBody(stop_type=StopSandboxBodyStopType.SHUTDOWN))


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
class CreateSnapshotParams:

    alias: str | None = None
    memory_snapshot: bool | None = None
    on_progress: Callable[[SnapshotProgress], None] | None = None

@dataclass
class BuildSnapshotParams(CreateSnapshotParams):
    dockerfile: str | None = None

# ─── Snapshot helpers ─────────────────────────────────────────────────────────

_CSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def _strip_ansi(s: str) -> str:
    return _CSI_RE.sub("", s)


def _base32_encode(s: str) -> str:
    return base64.b32encode(s.encode()).decode().lower().rstrip("=")


def _get_inferred_registry_url(base_url: str) -> str:
    hostname = urlparse(base_url).hostname or ""
    return hostname.replace("api.bartender.", "registry.")


def _is_local_environment(base_url: str) -> bool:
    return urlparse(base_url).hostname == "api.codesandbox.dev"


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

    async def from_build(
        self,
        docker_context: str,
        params: BuildSnapshotParams | None = None,
    ) -> CreateSnapshotResult:
        """Build a Docker image from an existing Dockerfile and register it as a snapshot."""
        if not await is_docker_available():
            raise RuntimeError(
                "Docker is not available. Please install Docker to use snapshot builds."
            )

        resolved_context = os.path.realpath(docker_context)
        resolved_dockerfile = os.path.realpath(params.dockerfile) if params and params.dockerfile else None
        
        architecture = (
            "arm64"
            if platform.machine().lower() == "arm64" and _is_local_environment(self._base_url)
            else "amd64"
        )

        async def noop() -> None:
            pass

        return await self._build_and_register(
            dockerfile_path=resolved_dockerfile,
            context=resolved_context,
            architecture=architecture,
            alias_default_namespace=os.path.basename(resolved_context),
            cleanup_fn=noop,
            params=params,
        )

    async def from_image(
        self,
        image: str,
        params: CreateSnapshotParams | None = None,
    ) -> CreateSnapshotResult:
        """Create a snapshot from a public Docker image without building."""
        # Parse the image reference into components
        ref = _parse_image_reference(image)

        def _emit(step: str, output: str) -> None:
            if params and params.on_progress:
                params.on_progress(SnapshotProgress(step=step, output=output))

        # Build CreateSnapshotBodyImage, mapping None to UNSET
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

        if params and params.alias:
            _emit("alias", "Creating alias...")
            namespace, alias_tag = _parse_alias(ref.name, params.alias)
            alias = f"{namespace}@{alias_tag}"
            await alias_snapshot_api(
                snapshot_data.id,
                client=self._api_client,
                body=AliasSnapshotBody(alias=alias),
            )

        return CreateSnapshotResult(snapshot_id=snapshot_id, alias=alias)

    # ─── Private helpers ──────────────────────────────────────────────────────

    async def _build_and_register(
        self,
        dockerfile_path: str | None,
        context: str,
        architecture: str,
        alias_default_namespace: str,
        cleanup_fn: Callable,
        params: CreateSnapshotParams | None,
    ) -> CreateSnapshotResult:
        try:
            meta_info = await _get_meta_info(self._api_key)
            team_id = meta_info.get("auth", {}).get("team")
            if not team_id:
                raise RuntimeError(
                    "Failed to fetch team information for the provided API key. "
                    "Please ensure your TOGETHER_API_KEY is correct and has access to a team."
                )

            repository = _base32_encode(team_id)
            registry = _get_inferred_registry_url(self._base_url)
            image_name = f"image-{uuid4()}".lower()
            image_tag = str(uuid4()).lower()
            full_image_name = f"{registry}/{repository}/{image_name}:{image_tag}"

            def _emit(step: str, output: str) -> None:
                if params and params.on_progress:
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

            if params and params.alias:
                _emit("alias", "Creating alias...")
                namespace, alias_tag = _parse_alias(alias_default_namespace, params.alias)
                alias = f"{namespace}@{alias_tag}"
                await alias_snapshot_api(
                    snapshot_data.id,
                    client=self._api_client,
                    body=AliasSnapshotBody(alias=alias),
                )

            return CreateSnapshotResult(snapshot_id=snapshot_id, alias=alias)

        finally:
            await cleanup_fn()


# ─── TogetherSandbox (main facade) ──────────────────────────────────────────


class TogetherSandbox:
    """
    The main entry point for the Together Sandbox SDK.

    Provides a unified interface over both the management API (sandboxes,
    VMs, templates) and the in-VM Sandbox API (files, execs, tasks).

    Example::

        sdk = TogetherSandbox(api_key="your-key")
        async with await sdk.sandboxes.start("sandbox-id") as sb:
            await sb.files.read_file("/package.json")

    Args:
        api_key: Together AI API key. Falls back to ``TOGETHER_API_KEY`` env var.
        base_url: Management API base URL. Defaults to ``https://api.bartender.codesandbox.io``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.bartender.codesandbox.stream",
    ) -> None:
        resolved_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not resolved_key:
            raise ValueError(
                "api_key must be provided or TOGETHER_API_KEY env var must be set"
            )
        self._api_key = resolved_key
        self._base_url = base_url
        self._api_client = ApiClient(
            base_url=base_url + "/api/v1",
            token=resolved_key,
            prefix="Bearer",
            raise_on_unexpected_status=True,
        )
        self.sandboxes = SandboxesNamespace(self._api_client)
        self.snapshots = SnapshotsNamespace(self._api_client, self._api_key, self._base_url)

    # NOTE: sdk.api_client is removed from the public surface.
    # The internal _api_client is still used by sandboxes and tokens namespaces.

    async def close(self) -> None:
        """Close the management API client."""
        await self._api_client.get_async_httpx_client().aclose()

    async def __aenter__(self) -> "TogetherSandbox":
        await self._api_client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._api_client.__aexit__(exc_type, exc_val, exc_tb)

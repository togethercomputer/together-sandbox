from __future__ import annotations

from typing import Any, AsyncIterator, List
from types import TracebackType

# ── Management API client ─────────────────────────────────────────────────────
from .api.client import AuthenticatedClient as ApiClient

# ── Management API endpoint functions ─────────────────────────────────────────
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

# ── Sandbox API models ────────────────────────────────────────────────────────
from .sandbox.models.create_exec_request import CreateExecRequest
from .sandbox.models.file_action_request import FileActionRequest
from .sandbox.models.file_action_request_action import FileActionRequestAction
from .sandbox.models.file_info import FileInfo
from .sandbox.models.exec_stdin import ExecStdin
from .sandbox.models.update_exec_request import UpdateExecRequest
from .sandbox.types import File

# ── SSE streaming helper ─────────────────────────────────────────────────────
from ._streaming import stream_sse_json


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

    async def list(self, path: str) -> list[FileInfo]:
        """List directory contents."""
        result = await list_directory_api(path, client=self._client)
        return result.files

    async def create(self, path: str) -> None:
        """Create a directory."""
        await create_directory_api(path, client=self._client)

    async def delete(self, path: str) -> None:
        """Delete a directory."""
        await delete_directory_api(path, client=self._client)

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
        from ._together_sandbox import TogetherSandbox
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
        from ._together_sandbox import TogetherSandbox
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
        from ._together_sandbox import TogetherSandbox
        sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        await sdk.sandboxes.shutdown(sandbox_id)
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

import os
from types import TracebackType
from typing import Any, AsyncIterator, List, Optional

# ── Management API client ─────────────────────────────────────────────────────
from .api.client import AuthenticatedClient as ApiClient

# ── Management API endpoint functions ─────────────────────────────────────────
from .api.api.vm.vmstart import asyncio as vm_start_api
from .api.api.vm.vmhibernate import asyncio as vm_hibernate_api
from .api.api.vm.vmshutdown import asyncio as vm_shutdown_api
from .api.api.sandbox.sandboxfork import asyncio as sandbox_fork_api
from .api.api.default.preview_tokenlist import asyncio as preview_token_list_api
from .api.api.default.preview_tokencreate import asyncio as preview_token_create_api
from .api.api.default.preview_tokenupdate import asyncio as preview_token_update_api
from .api.api.default.preview_tokenrevoke_all import asyncio as preview_token_revoke_all_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.preview_token_create_request import PreviewTokenCreateRequest
from .api.models.preview_token_create_response import PreviewTokenCreateResponse
from .api.models.preview_token_list_response import PreviewTokenListResponse
from .api.models.preview_token_revoke_all_response import PreviewTokenRevokeAllResponse
from .api.models.preview_token_update_request import PreviewTokenUpdateRequest
from .api.models.preview_token_update_response import PreviewTokenUpdateResponse
from .api.models.vm_start_request import VMStartRequest
from .api.models.vm_start_response_data import VMStartResponseData
from .api.types import UNSET

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
from .sandbox.models.file_action_request import FileActionRequest
from .sandbox.models.file_action_request_action import FileActionRequestAction
from .sandbox.models.file_action_response import FileActionResponse
from .sandbox.models.file_create_request import FileCreateRequest
from .sandbox.models.file_info import FileInfo
from .sandbox.models.file_operation_response import FileOperationResponse
from .sandbox.models.file_read_response import FileReadResponse
from .sandbox.models.exec_stdin import ExecStdin
from .sandbox.models.task_action_type import TaskActionType

# ── SSE streaming helper ─────────────────────────────────────────────────────
from ._streaming import stream_sse_json


# ─── Internal helpers ─────────────────────────────────────────────────────────


def _resolve_connection(vm_info: VMStartResponseData) -> tuple[str, str]:
    """
    Select the appropriate (url, token) pair from the vmStart response.
    Prefers Pint when available, falls back to Pitcher (legacy agent).
    """
    if vm_info.use_pint and vm_info.pint_url is not UNSET and vm_info.pint_token is not UNSET:
        return vm_info.pint_url, vm_info.pint_token
    return vm_info.pitcher_url, vm_info.pitcher_token


# ─── Files facade ─────────────────────────────────────────────────────────────


class FilesFacade:
    """
    File operations facade that wraps the low-level files client.

    Adds ``move_file``, ``copy_file``, and ``watch`` methods while
    delegating existing methods to the underlying client.
    """

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def read_file(self, path: str) -> FileReadResponse:
        """Read file content at the specified path."""
        return await read_file_api(path, client=self._client)

    async def create_file(
        self, path: str, body: FileCreateRequest | None = None
    ) -> FileReadResponse:
        """Create a file at the specified path with optional content."""
        return await create_file_api(path, client=self._client, body=body)

    async def delete_file(self, path: str) -> FileOperationResponse:
        """Delete a file at the specified path."""
        return await delete_file_api(path, client=self._client)

    async def move_file(self, from_path: str, to_path: str) -> FileActionResponse:
        """Move a file from one path to another."""
        return await perform_file_action_api(
            from_path,
            client=self._client,
            body=FileActionRequest(
                action=FileActionRequestAction.MOVE,
                destination=to_path,
            ),
        )

    async def copy_file(self, from_path: str, to_path: str) -> FileActionResponse:
        """Copy a file from one path to another."""
        return await perform_file_action_api(
            from_path,
            client=self._client,
            body=FileActionRequest(
                action=FileActionRequestAction.COPY,
                destination=to_path,
            ),
        )

    async def get_file_stat(self, path: str) -> FileInfo:
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


class ExecsFacade:
    """
    Exec operations facade with renamed SSE methods.

    - ``get_exec_output`` → ``stream_output``
    - ``exec_exec_stdin`` → ``send_stdin``
    - ``stream_execs_list`` → ``stream_list``
    - ``connect_to_exec_web_socket`` → removed
    """

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list_execs(self):
        """List all active execs."""
        return await list_execs_api(client=self._client)

    async def create_exec(self, body):
        """Create a new exec."""
        return await create_exec_api(client=self._client, body=body)

    async def get_exec(self, id_: str):
        """Get exec by ID."""
        return await get_exec_api(id_, client=self._client)

    async def update_exec(self, id_: str, body):
        """Update exec status."""
        return await update_exec_api(id_, client=self._client, body=body)

    async def delete_exec(self, id_: str):
        """Delete an exec."""
        return await delete_exec_api(id_, client=self._client)

    def stream_output(
        self, id_: str, last_sequence: int | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream exec output via SSE (renamed from get_exec_output)."""
        params: dict[str, Any] = {}
        if last_sequence is not None:
            params["lastSequence"] = last_sequence
        return stream_sse_json(
            self._client.get_async_httpx_client(),
            f"/api/v1/execs/{id_}/io",
            params=params,
        )

    async def send_stdin(self, id_: str, body: ExecStdin):
        """Send stdin to an exec (renamed from exec_exec_stdin)."""
        return await exec_exec_stdin_api(id_, client=self._client, body=body)

    def stream_list(self) -> AsyncIterator[dict[str, Any]]:
        """Stream list of all active execs via SSE (renamed from stream_execs_list)."""
        return stream_sse_json(
            self._client.get_async_httpx_client(),
            "/api/v1/stream/execs",
        )


# ─── Ports facade ─────────────────────────────────────────────────────────────


class PortsFacade:
    """
    Port operations facade with renamed SSE method.

    - ``stream_ports_list`` → ``stream_list``
    """

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list_ports(self):
        """List open ports."""
        return await list_ports_api(client=self._client)

    def stream_list(self) -> AsyncIterator[dict[str, Any]]:
        """Stream port changes via SSE (renamed from stream_ports_list)."""
        return stream_sse_json(
            self._client.get_async_httpx_client(),
            "/api/v1/stream/ports",
        )


# ─── Directories facade ──────────────────────────────────────────────────────


class DirectoriesFacade:
    """Directory operations (list, create, delete)."""

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list_directory(self, path: str):
        """List directory contents."""
        return await list_directory_api(path, client=self._client)

    async def create_directory(self, path: str):
        """Create a directory."""
        return await create_directory_api(path, client=self._client)

    async def delete_directory(self, path: str):
        """Delete a directory."""
        return await delete_directory_api(path, client=self._client)


# ─── Tasks facade ─────────────────────────────────────────────────────────────


class TasksFacade:
    """Task operations (list, list_setup, get, action)."""

    def __init__(self, sandbox_client: SandboxClient) -> None:
        self._client = sandbox_client

    async def list_tasks(self):
        """List all tasks."""
        return await list_tasks_api(client=self._client)

    async def list_setup_tasks(self):
        """List setup tasks."""
        return await list_setup_tasks_api(client=self._client)

    async def get_task(self, id_: str):
        """Get task by ID."""
        return await get_task_api(id_, client=self._client)

    async def execute_task_action(self, id_: str, action_type: TaskActionType):
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
        vm_info: VMStartResponseData,
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
        return self._vm_info.id

    @property
    def vm_info(self) -> VMStartResponseData:
        """Raw VM start response (id, cluster, workspace_path, etc.)."""
        return self._vm_info

    # ── Sandbox sub-namespace delegation ──────────────────────────────────────

    @property
    def files(self) -> FilesFacade:
        """File system operations (read, create, delete, move, copy, stat, watch)."""
        return FilesFacade(self._sandbox_client)

    @property
    def directories(self) -> DirectoriesFacade:
        """Directory operations (list, create, delete)."""
        return DirectoriesFacade(self._sandbox_client)

    @property
    def execs(self) -> ExecsFacade:
        """Shell exec operations (create, get, update, stream_output, send_stdin, stream_list)."""
        return ExecsFacade(self._sandbox_client)

    @property
    def tasks(self) -> TasksFacade:
        """Task operations (list, list_setup, get, action)."""
        return TasksFacade(self._sandbox_client)

    @property
    def ports(self) -> PortsFacade:
        """Port discovery (list, stream_list)."""
        return PortsFacade(self._sandbox_client)

    # NOTE: sandbox.streams is removed — use sandbox.files.watch() instead

    # ── Lifecycle methods ─────────────────────────────────────────────────────

    async def hibernate(self) -> None:
        """Suspend (hibernate) this VM."""
        await vm_hibernate_api(self.id, client=self._api_client)

    async def shutdown(self) -> None:
        """Shut down this VM."""
        await vm_shutdown_api(self.id, client=self._api_client)

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
        start_options: VMStartRequest | None = None,
    ) -> "Sandbox":
        """
        Start a sandbox in a single call (classmethod factory).

        Example::

            sandbox = await Sandbox.start("sandbox-id", api_key="your-key")
        """
        sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        return await sdk.sandboxes.start(sandbox_id, start_options=start_options)


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
        start_options: VMStartRequest | None = None,
    ) -> Sandbox:
        """
        Start the VM for the given sandbox and return a :class:`Sandbox`
        with a fully wired sandbox client.

        The ``pint_url``/``pint_token`` vs. ``pitcher_url``/``pitcher_token``
        selection is handled automatically based on the ``use_pint`` flag.

        Args:
            sandbox_id: The sandbox (VM) ID to start.
            start_options: Optional :class:`VMStartRequest` for tier/wakeup config.

        Returns:
            A ready-to-use :class:`Sandbox` with all sub-namespaces.
        """
        response = await vm_start_api(sandbox_id, client=self._api_client, body=start_options)
        vm_info = response.data

        if vm_info is None or isinstance(vm_info, type(UNSET)):
            raise RuntimeError(
                f"vmStart for sandbox '{sandbox_id}' returned no data. "
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

    async def fork(
        self,
        sandbox_id: str,
        *,
        fork_options: Any = None,
    ) -> Sandbox:
        """
        Fork an existing sandbox and immediately start its VM.

        Args:
            sandbox_id: The sandbox to fork.
            fork_options: Optional fork request body.

        Returns:
            A :class:`Sandbox` for the newly forked + started sandbox.
        """
        fork_response = await sandbox_fork_api(sandbox_id, client=self._api_client, body=fork_options)
        new_id = fork_response.data.id
        return await self.start(new_id)

    async def hibernate(self, sandbox_id: str) -> None:
        """Hibernate (suspend) a VM by sandbox ID."""
        await vm_hibernate_api(sandbox_id, client=self._api_client)

    async def shutdown(self, sandbox_id: str) -> None:
        """Shut down a VM by sandbox ID."""
        await vm_shutdown_api(sandbox_id, client=self._api_client)


# ─── TokensNamespace ──────────────────────────────────────────────────────────


class TokensNamespace:
    """
    Preview token operations accessed as ``sdk.tokens.*``.

    Preview tokens allow access to private sandboxes.
    """

    def __init__(self, api_client: ApiClient) -> None:
        self._api_client = api_client

    async def list(self, sandbox_id: str) -> PreviewTokenListResponse:
        """List all preview tokens for a sandbox."""
        return await preview_token_list_api(sandbox_id, client=self._api_client)

    async def create(
        self, sandbox_id: str, body: PreviewTokenCreateRequest | None = None
    ) -> PreviewTokenCreateResponse:
        """Create a new preview token for a sandbox."""
        return await preview_token_create_api(sandbox_id, client=self._api_client, body=body)

    async def update(
        self,
        sandbox_id: str,
        token_id: str,
        body: PreviewTokenUpdateRequest | None = None,
    ) -> PreviewTokenUpdateResponse:
        """Update an existing preview token."""
        return await preview_token_update_api(
            sandbox_id, token_id, client=self._api_client, body=body
        )

    async def revoke_all(self, sandbox_id: str) -> PreviewTokenRevokeAllResponse:
        """Revoke all preview tokens for a sandbox."""
        return await preview_token_revoke_all_api(sandbox_id, client=self._api_client)


# ─── TogetherSandbox (main facade) ───────────────────────────────────────────


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
        base_url: Management API base URL. Defaults to ``https://api.codesandbox.io``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.codesandbox.io",
    ) -> None:
        resolved_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not resolved_key:
            raise ValueError(
                "api_key must be provided or TOGETHER_API_KEY env var must be set"
            )
        self._api_client = ApiClient(
            base_url=base_url,
            token=resolved_key,
            prefix="Bearer",
            raise_on_unexpected_status=True,
        )
        self.sandboxes = SandboxesNamespace(self._api_client)
        self.tokens = TokensNamespace(self._api_client)

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

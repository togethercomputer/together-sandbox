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
from typing import Any, Optional

from .api.client import APIClient as ApiClient
from .api.endpoints.sandbox import SandboxClient as SandboxEndpointClient
from .api.models.vm_start_request_2 import VmStartRequest2
from .api.models.vm_start_response_data_2 import VmStartResponseData2
from .core.config import ClientConfig
from .core.http_transport import HttpxTransport
from .sandbox.client import APIClient as SandboxClient


# ─── Internal helpers ─────────────────────────────────────────────────────────


def _resolve_connection(vm_info: VmStartResponseData2) -> tuple[str, str]:
    """
    Select the appropriate (url, token) pair from the vmStart response.
    Prefers Pint when available, falls back to Pitcher (legacy agent).
    """
    if vm_info.use_pint and vm_info.pint_url and vm_info.pint_token:
        return vm_info.pint_url, vm_info.pint_token
    return vm_info.pitcher_url, vm_info.pitcher_token


# ─── Sandbox (connected sandbox) ─────────────────────────────────────────────


class Sandbox:
    """
    A running VM with a fully-initialized sandbox client attached.

    Access sandbox operations through the sub-namespaces::

        await sandbox.files.read_file("/path")
        await sandbox.execs.create_exec(CreateExecRequest(...))
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
        vm_info: VmStartResponseData2,
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
        return self._vm_info.id_

    @property
    def vm_info(self) -> VmStartResponseData2:
        """Raw VM start response (id, cluster, workspace_path, etc.)."""
        return self._vm_info

    @property
    def sandbox_client(self) -> SandboxClient:
        """The underlying SandboxClient, exposed for advanced/low-level use."""
        return self._sandbox_client

    # ── Sandbox sub-namespace delegation ──────────────────────────────────────

    @property
    def files(self):
        """File system operations (read, create, delete, move)."""
        return self._sandbox_client.files

    @property
    def directories(self):
        """Directory operations (list, create, delete)."""
        return self._sandbox_client.directories

    @property
    def execs(self):
        """Shell exec operations (create, get, update, stream)."""
        return self._sandbox_client.execs

    @property
    def tasks(self):
        """Task operations (list, get, action)."""
        return self._sandbox_client.tasks

    @property
    def ports(self):
        """Port discovery (list, stream)."""
        return self._sandbox_client.ports

    @property
    def streams(self):
        """SSE stream helpers."""
        return self._sandbox_client.streams

    # ── Lifecycle methods ─────────────────────────────────────────────────────

    async def hibernate(self) -> None:
        """Suspend (hibernate) this VM."""
        await self._api_client.vm.vm_hibernate(self.id)

    async def shutdown(self) -> None:
        """Shut down this VM."""
        await self._api_client.vm.vm_shutdown(self.id)

    async def close(self) -> None:
        """Close the underlying sandbox client connection."""
        await self._sandbox_client.close()

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

    # ── Static factory (convenience classmethod) ────────────────────────────────

    @classmethod
    async def start(
        cls,
        sandbox_id: str,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.codesandbox.io",
        start_options: VmStartRequest2 | None = None,
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
        start_options: VmStartRequest2 | None = None,
    ) -> Sandbox:
        """
        Start the VM for the given sandbox and return a :class:`Sandbox`
        with a fully wired sandbox client.

        The ``pint_url``/``pint_token`` vs. ``pitcher_url``/``pitcher_token``
        selection is handled automatically based on the ``use_pint`` flag.

        Args:
            sandbox_id: The sandbox (VM) ID to start.
            start_options: Optional :class:`VmStartRequest2` for tier/wakeup config.

        Returns:
            A ready-to-use :class:`Sandbox` with all sub-namespaces.
        """
        response = await self._api_client.vm.vm_start(sandbox_id, body=start_options)
        vm_info = response.data_

        if vm_info is None:
            raise RuntimeError(
                f"vmStart for sandbox '{sandbox_id}' returned no data. "
                "Check that the sandbox ID is valid and your API key has the required scopes."
            )

        url, token = _resolve_connection(vm_info)

        sandbox_client = SandboxClient(
            ClientConfig(base_url=url),
            transport=HttpxTransport(url, bearer_token=token),
        )

        return Sandbox(vm_info, sandbox_client, self._api_client)

    async def fork(
        self,
        sandbox_id: str,
        *,
        fork_options: Any = None,
        start_options: VmStartRequest2 | None = None,
    ) -> Sandbox:
        """
        Fork an existing sandbox and immediately start its VM.

        Args:
            sandbox_id: The sandbox to fork.
            fork_options: Optional fork request body.
            start_options: Optional :class:`VmStartRequest2` for the resulting VM.

        Returns:
            A :class:`Sandbox` for the newly forked + started sandbox.
        """
        fork_response = await self._api_client.sandbox.sandbox_fork(
            sandbox_id, body=fork_options
        )
        new_id = fork_response.data_.id_
        return await self.start(new_id, start_options=start_options)


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
            ClientConfig(base_url=base_url),
            transport=HttpxTransport(base_url, bearer_token=resolved_key),
        )
        self.sandboxes = SandboxesNamespace(self._api_client)

    @property
    def api_client(self) -> ApiClient:
        """The underlying management API client (for advanced use)."""
        return self._api_client

    async def close(self) -> None:
        """Close the management API client."""
        await self._api_client.close()

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

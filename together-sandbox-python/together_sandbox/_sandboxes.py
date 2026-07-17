from __future__ import annotations

from .api.client import AuthenticatedClient as ApiClient

from ._sandbox import Sandbox

# ── Management API endpoint functions (detailed variants) ─────────────────────
from .api.api.default.start_sandbox import asyncio_detailed as start_sandbox_api
from .api.api.default.wait_for_sandbox import asyncio_detailed as wait_for_sandbox_api
from .api.api.default.stop_sandbox import asyncio_detailed as stop_sandbox_api
from .api.api.default.create_sandbox import asyncio_detailed as create_sandbox_api
from .api.api.default.list_sandboxes import asyncio_detailed as list_sandboxes_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.sandbox import Sandbox as SandboxModel
from .api.models.stop_sandbox_body import StopSandboxBody
from .api.models.stop_sandbox_body_stop_type import StopSandboxBodyStopType
from .api.models.create_sandbox_body import CreateSandboxBody
from .api.models.start_sandbox_body import StartSandboxBody
from .api.types import UNSET

# ── Helpers ─────────────────────────────────────────────────────
from ._utils import RetryConfig, _call_api, _resolve_connection
from ._pagination import Page
from ._lifecycle import describe_lifecycle_failure

# ── Sandbox API client ────────────────────────────────────────────────────────
from .sandbox.client import AuthenticatedClient as SandboxClient

# Default sandbox resource allocation. Match the TS SDK / CLI helper.
DEFAULT_MILLICPU = 1000  # 1 vCPU
DEFAULT_MEMORY_BYTES = 2048 * 1024 * 1024  # 2 GiB
DEFAULT_DISK_BYTES = 10240 * 1024 * 1024  # 10 GiB


async def _connect_running_sandbox(
    sandbox_id: str,
    api_client: ApiClient,
    retry: RetryConfig | None,
) -> Sandbox:
    """Wait for a sandbox to reach 'running', wire up its client, and return it.

    Shared by :meth:`SandboxesNamespace.create` and :meth:`SandboxesNamespace.start`.
    """
    vm_info: SandboxModel = await _call_api(
        "api.wait_for_sandbox",
        lambda: wait_for_sandbox_api(sandbox_id, client=api_client),
        retry,
        context=f"for sandbox {sandbox_id!r}",
    )

    if vm_info.status != "running":
        raise RuntimeError(describe_lifecycle_failure(vm_info, "running"))

    url, token = _resolve_connection(vm_info)

    sandbox_client = SandboxClient(
        base_url=url,
        token=token,
        prefix="Bearer",
    )

    return Sandbox(vm_info, sandbox_client, api_client, retry=retry)


class SandboxesNamespace:
    """Sandbox lifecycle operations accessed as ``sdk.sandboxes.*``."""

    def __init__(
        self,
        api_client: ApiClient,
        *,
        retry: RetryConfig | None = None,
    ) -> None:
        self._api_client = api_client
        self._retry = retry

    async def start(
        self,
        sandbox_id: str,
        *,
        version_number: int | None = None,
    ) -> Sandbox:
        """
        Start the VM for the given sandbox and return a :class:`Sandbox`
        with a fully wired sandbox client.

        Args:
            sandbox_id: The sandbox (VM) ID to start.
            version_number: Optional version number to start. Uses the current
                version if not provided.

        Returns:
            A ready-to-use :class:`Sandbox` with all sub-namespaces.
        """
        body = (
            UNSET
            if version_number is None
            else StartSandboxBody(version_number=version_number)
        )

        await _call_api(
            "api.start_sandbox",
            lambda: start_sandbox_api(sandbox_id, client=self._api_client, body=body),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        return await _connect_running_sandbox(sandbox_id, self._api_client, self._retry)

    async def create(
        self,
        *,
        millicpu: int = DEFAULT_MILLICPU,
        memory_bytes: int = DEFAULT_MEMORY_BYTES,
        disk_bytes: int = DEFAULT_DISK_BYTES,
        id: str | None = None,
        snapshot_id: str | None = None,
        snapshot_alias: str | None = None,
        ephemeral: bool | None = None,
    ) -> Sandbox:
        """Create a sandbox and wait for it to be running.

        Args:
            millicpu: CPU allocation in millicores (e.g. 1000 = 1 vCPU).
            memory_bytes: Memory allocation in bytes.
            disk_bytes: Disk allocation in bytes.
            id: Optional explicit sandbox ID.
            snapshot_id: Optional snapshot ID to create the sandbox from.
            snapshot_alias: Optional snapshot alias to create the sandbox from.
            ephemeral: Optional flag to mark the sandbox as ephemeral.

        """
        body = CreateSandboxBody(
            id=id if id is not None else UNSET,
            snapshot_id=snapshot_id if snapshot_id is not None else UNSET,
            snapshot_alias=snapshot_alias if snapshot_alias is not None else UNSET,
            ephemeral=ephemeral if ephemeral is not None else UNSET,
            autostart=True,
            millicpu=millicpu,
            memory_bytes=memory_bytes,
            disk_bytes=disk_bytes,
        )
        sandbox_model: SandboxModel = await _call_api(
            "api.create_sandbox",
            lambda: create_sandbox_api(client=self._api_client, body=body),
            self._retry,
        )

        return await _connect_running_sandbox(sandbox_model.id, self._api_client, self._retry)

    async def list(
        self, *, limit: int | None = None, project_id: str | None = None
    ) -> Page[SandboxModel]:
        """List sandboxes.

        Returns a :class:`Page` that is async-iterable across all pages —
        iterate it directly to walk every sandbox, or use ``get_next_page()``
        / ``next_cursor`` for manual page-by-page control.

        Args:
            limit: Max items per page (1–100, default 20).
            project_id: Filter to a single project.

        Returns:
            Page[Sandbox]: First page of sandboxes.

        Example:
            >>> async for sandbox in await sdk.sandboxes.list():
            ...     print(sandbox.id)
        """

        async def fetch_page(cursor: str | None = None) -> Page[SandboxModel]:
            result = await _call_api(
                "api.list_sandboxes",
                lambda: list_sandboxes_api(
                    client=self._api_client,
                    limit=limit if limit is not None else UNSET,
                    cursor=cursor if cursor is not None else UNSET,
                    project_id=project_id if project_id is not None else UNSET,
                ),
                self._retry,
            )
            return Page(result.data, result.next_cursor, fetch_page)

        return await fetch_page()

    async def hibernate(self, sandbox_id: str) -> None:
        """Hibernate (suspend) a VM by sandbox ID."""
        await _call_api(
            "api.stop_sandbox",
            lambda: stop_sandbox_api(
                sandbox_id,
                client=self._api_client,
                body=StopSandboxBody(stop_type=StopSandboxBodyStopType.HIBERNATE),
            ),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        vm_info: SandboxModel = await _call_api(
            "api.wait_for_sandbox",
            lambda: wait_for_sandbox_api(sandbox_id, client=self._api_client),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        if vm_info.status != "stopped":
            raise RuntimeError(describe_lifecycle_failure(vm_info, "stopped"))

    async def shutdown(self, sandbox_id: str) -> None:
        """Shut down a VM by sandbox ID."""
        await _call_api(
            "api.stop_sandbox",
            lambda: stop_sandbox_api(
                sandbox_id,
                client=self._api_client,
                body=StopSandboxBody(stop_type=StopSandboxBodyStopType.SHUTDOWN),
            ),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        vm_info: SandboxModel = await _call_api(
            "api.wait_for_sandbox",
            lambda: wait_for_sandbox_api(sandbox_id, client=self._api_client),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        if vm_info.status != "stopped":
            raise RuntimeError(describe_lifecycle_failure(vm_info, "stopped"))

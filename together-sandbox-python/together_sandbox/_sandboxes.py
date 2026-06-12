from __future__ import annotations

from .api.client import AuthenticatedClient as ApiClient

from ._sandbox import Sandbox

# ── Management API endpoint functions (detailed variants) ─────────────────────
from .api.api.default.start_sandbox import asyncio_detailed as start_sandbox_api
from .api.api.default.wait_for_sandbox import asyncio_detailed as wait_for_sandbox_api
from .api.api.default.stop_sandbox import asyncio_detailed as stop_sandbox_api
from .api.api.default.create_sandbox import asyncio_detailed as create_sandbox_api
from .api.api.default.list_sandboxes import asyncio_detailed as list_sandboxes_api
from .api.api.default.get_sandbox import asyncio_detailed as get_sandbox_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.sandbox import Sandbox as SandboxModel

# Public alias for the raw sandbox metadata model returned by list/get endpoints.
# Named separately from the ``Sandbox`` runtime class (a wired client).
SandboxRecord = SandboxModel
from .api.models.stop_sandbox_body import StopSandboxBody
from .api.models.stop_sandbox_body_stop_type import StopSandboxBodyStopType
from .api.models.create_sandbox_body import CreateSandboxBody
from .api.models.start_sandbox_body import StartSandboxBody
from .api.types import UNSET

# ── Helpers ─────────────────────────────────────────────────────
from ._utils import RetryConfig, _call_api, _resolve_connection
from ._lifecycle import describe_lifecycle_failure
from ._pagination import Page

# ── Sandbox API client ────────────────────────────────────────────────────────
from .sandbox.client import AuthenticatedClient as SandboxClient

# Default sandbox resource allocation. Match the TS SDK / CLI helper.
DEFAULT_MILLICPU = 1000  # 1 vCPU
DEFAULT_MEMORY_BYTES = 2048 * 1024 * 1024  # 2 GiB
DEFAULT_DISK_BYTES = 10240 * 1024 * 1024  # 10 GiB


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

        vm_info: SandboxModel = await _call_api(
            "api.wait_for_sandbox",
            lambda: wait_for_sandbox_api(sandbox_id, client=self._api_client),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        if vm_info.status != "running":
            raise RuntimeError(describe_lifecycle_failure(vm_info, "running"))

        url, token = _resolve_connection(vm_info)

        sandbox_client = SandboxClient(
            base_url=url,
            token=token,
            prefix="Bearer",
            # raise_on_unexpected_status omitted — _call_api owns error handling.
        )

        return Sandbox(vm_info, sandbox_client, self._api_client, retry=self._retry)

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
    ) -> SandboxModel:
        """Create a new sandbox (does not start the VM).

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
            millicpu=millicpu,
            memory_bytes=memory_bytes,
            disk_bytes=disk_bytes,
        )
        return await _call_api(
            "api.create_sandbox",
            lambda: create_sandbox_api(client=self._api_client, body=body),
            self._retry,
        )

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        project_id: str | None = None,
    ) -> Page[SandboxRecord]:
        """List sandboxes, one page at a time.

        Args:
            limit: Maximum number of items to return (1–100, default 20).
            cursor: A ``next_cursor`` value returned by a previous page.
            project_id: Restrict results to a specific project.

        Returns:
            Page[SandboxRecord]: A page of sandboxes. Pass ``page.next_cursor``
            back as ``cursor`` to fetch the next page; it is ``None`` on the
            last page.

        Raises:
            HttpError: If the API request fails.

        Example:
            >>> page = await sdk.sandboxes.list(limit=20)
            >>> for sandbox in page.data:
            ...     print(sandbox.id)
            >>> if page.next_cursor:
            ...     page = await sdk.sandboxes.list(cursor=page.next_cursor)
        """
        resp = await _call_api(
            "api.list_sandboxes",
            lambda: list_sandboxes_api(
                client=self._api_client,
                limit=UNSET if limit is None else limit,
                cursor=UNSET if cursor is None else cursor,
                project_id=UNSET if project_id is None else project_id,
            ),
            self._retry,
        )
        return Page(data=resp.data, next_cursor=resp.next_cursor)

    async def get(self, id: str) -> SandboxRecord:
        """Fetch a single sandbox by id.

        Args:
            id: The sandbox id.

        Returns:
            SandboxRecord: The raw sandbox metadata model.

        Raises:
            HttpError: If the API request fails (e.g. the sandbox is not found).
        """
        return await _call_api(
            "api.get_sandbox",
            lambda: get_sandbox_api(id, client=self._api_client),
            self._retry,
            context=f"for sandbox {id!r}",
        )

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

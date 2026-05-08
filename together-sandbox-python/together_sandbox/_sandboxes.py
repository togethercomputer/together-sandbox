from __future__ import annotations

from .api.client import AuthenticatedClient as ApiClient

from ._sandbox import Sandbox

# ── Management API endpoint functions (detailed variants) ─────────────────────
from .api.api.default.start_sandbox import asyncio_detailed as start_sandbox_api
from .api.api.default.wait_for_sandbox import asyncio_detailed as wait_for_sandbox_api
from .api.api.default.stop_sandbox import asyncio_detailed as stop_sandbox_api
from .api.api.default.create_sandbox import asyncio_detailed as create_sandbox_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.sandbox import Sandbox as SandboxModel
from .api.models.stop_sandbox_body import StopSandboxBody
from .api.models.stop_sandbox_body_stop_type import StopSandboxBodyStopType
from .api.models.create_sandbox_body import CreateSandboxBody
from .api.models.start_sandbox_body import StartSandboxBody
from .api.types import UNSET

# ── Retry / call helper ───────────────────────────────────────────────────────
from ._utils import RetryConfig, _call_api

# ── Sandbox API client ────────────────────────────────────────────────────────
from .sandbox.client import AuthenticatedClient as SandboxClient


def _resolve_connection(sandbox: SandboxModel) -> tuple[str, str]:
    """Extract the agent connection details from the Sandbox model."""
    if not sandbox.agent_url or not sandbox.agent_token:
        raise RuntimeError("Sandbox has no agent connection details")
    return sandbox.agent_url, sandbox.agent_token


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
            "sandboxes.start",
            lambda: start_sandbox_api(sandbox_id, client=self._api_client, body=body),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        vm_info: SandboxModel = await _call_api(
            "sandboxes.wait",
            lambda: wait_for_sandbox_api(sandbox_id, client=self._api_client),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        if vm_info.status != "running":
            raise RuntimeError(
                f"Failed to start sandbox '{sandbox_id}'. Its final status was {vm_info.status}."
            )

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
        millicpu: int,
        memory_bytes: int,
        disk_bytes: int,
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
            "sandboxes.create",
            lambda: create_sandbox_api(client=self._api_client, body=body),
            self._retry,
        )

    async def hibernate(self, sandbox_id: str) -> None:
        """Hibernate (suspend) a VM by sandbox ID."""
        await _call_api(
            "sandboxes.hibernate",
            lambda: stop_sandbox_api(
                sandbox_id,
                client=self._api_client,
                body=StopSandboxBody(stop_type=StopSandboxBodyStopType.HIBERNATE),
            ),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        vm_info: SandboxModel = await _call_api(
            "sandboxes.wait",
            lambda: wait_for_sandbox_api(sandbox_id, client=self._api_client),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        if vm_info.status != "stopped":
            raise RuntimeError(
                f"Failed to hibernate sandbox '{sandbox_id}'. Its final status was {vm_info.status}."
            )

    async def shutdown(self, sandbox_id: str) -> None:
        """Shut down a VM by sandbox ID."""
        await _call_api(
            "sandboxes.shutdown",
            lambda: stop_sandbox_api(
                sandbox_id,
                client=self._api_client,
                body=StopSandboxBody(stop_type=StopSandboxBodyStopType.SHUTDOWN),
            ),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        vm_info: SandboxModel = await _call_api(
            "sandboxes.wait",
            lambda: wait_for_sandbox_api(sandbox_id, client=self._api_client),
            self._retry,
            context=f"for sandbox {sandbox_id!r}",
        )

        if vm_info.status != "stopped":
            raise RuntimeError(
                f"Failed to stop sandbox '{sandbox_id}'. Its final status was {vm_info.status}."
            )

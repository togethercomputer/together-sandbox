from __future__ import annotations

from .api.client import AuthenticatedClient as ApiClient

from ._sandbox import Sandbox
from ._types import CreateSandboxParams, StartOptions

# ── Management API endpoint functions ─────────────────────────────────────────
from .api.api.default.start_sandbox import asyncio as start_sandbox_api
from .api.api.default.stop_sandbox import asyncio as stop_sandbox_api
from .api.api.default.create_sandbox import asyncio as create_sandbox_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.sandbox import Sandbox as SandboxModel
from .api.models.stop_sandbox_body import StopSandboxBody
from .api.models.stop_sandbox_body_stop_type import StopSandboxBodyStopType
from .api.models.create_sandbox_body import CreateSandboxBody
from .api.models.start_sandbox_body import StartSandboxBody

# ── Sandbox API client ────────────────────────────────────────────────────────
from .sandbox.client import AuthenticatedClient as SandboxClient

def _resolve_connection(sandbox: SandboxModel) -> tuple[str, str]:
    """
    Extract the agent connection details from the Sandbox model.
    """
    if not sandbox.agent_url or not sandbox.agent_token:
        raise RuntimeError("Sandbox has no agent connection details")
    return sandbox.agent_url, sandbox.agent_token




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
        start_options: StartOptions | None = None,
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
        body = None
        if start_options is not None:
            body = StartSandboxBody(version_number=start_options.version_number)
        response = await start_sandbox_api(sandbox_id, client=self._api_client, body=body)
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

    async def create(self, params: CreateSandboxParams) -> SandboxModel:
        """Create a new sandbox (does not start the VM)."""
        body = CreateSandboxBody(
            id=params.id,
            snapshot_id=params.snapshot_id,
            snapshot_alias=params.snapshot_alias,
            ephemeral=params.ephemeral,
            millicpu=params.millicpu,
            memory_bytes=params.memory_bytes,
            disk_bytes=params.disk_bytes,
        )
        result = await create_sandbox_api(client=self._api_client, body=body)
        if result is None:
            raise RuntimeError("createSandbox returned None")
        return result

    async def hibernate(self, sandbox_id: str) -> None:
        """Hibernate (suspend) a VM by sandbox ID."""
        await stop_sandbox_api(sandbox_id, client=self._api_client,
                               body=StopSandboxBody(stop_type=StopSandboxBodyStopType.HIBERNATE))

    async def shutdown(self, sandbox_id: str) -> None:
        """Shut down a VM by sandbox ID."""
        await stop_sandbox_api(sandbox_id, client=self._api_client,
                               body=StopSandboxBody(stop_type=StopSandboxBodyStopType.SHUTDOWN))
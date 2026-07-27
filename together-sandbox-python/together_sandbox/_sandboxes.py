from __future__ import annotations

from .api.client import AuthenticatedClient as ApiClient

from ._sandbox import Sandbox

# ── Management API endpoint functions (detailed variants) ─────────────────────
from .api.api.default.wait_for_sandbox import asyncio_detailed as wait_for_sandbox_api
from .api.api.default.terminate_sandbox import asyncio_detailed as terminate_sandbox_api
from .api.api.default.create_sandbox import asyncio_detailed as create_sandbox_api
from .api.api.default.list_sandboxes import asyncio_detailed as list_sandboxes_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.sandbox import Sandbox as SandboxModel
from .api.models.terminate_sandbox_body import TerminateSandboxBody
from .api.models.create_sandbox_body import CreateSandboxBody
from .api.models.create_sandbox_body_tags import CreateSandboxBodyTags
from .api.types import UNSET, Unset

# ── Helpers ─────────────────────────────────────────────────────
from ._utils import (
    RetryConfig,
    _call_api,
    _resolve_connection,
    build_termination_policy,
    build_termination_snapshot,
)
from ._pagination import Page
from ._lifecycle import describe_lifecycle_failure

# ── Sandbox API client ────────────────────────────────────────────────────────
from .sandbox.client import AuthenticatedClient as SandboxClient

# Default sandbox resource allocation. Match the TS SDK / CLI helper.
DEFAULT_CPU = 1.0  # 1 vCPU (cores)
DEFAULT_MEMORY_BYTES = 2048 * 1024 * 1024  # 2 GiB


async def _connect_running_sandbox(
    sandbox_id: str,
    api_client: ApiClient,
    retry: RetryConfig | None,
) -> Sandbox:
    """Wait for a sandbox to reach 'running', wire up its client, and return it.

    Used by :meth:`SandboxesNamespace.create`.
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

    async def create(
        self,
        *,
        cpu: float = DEFAULT_CPU,
        memory_bytes: int = DEFAULT_MEMORY_BYTES,
        snapshot_id: str | None = None,
        snapshot_alias: str | None = None,
        ttl: int | None = None,
        tags: dict[str, str] | None = None,
        termination_policy: dict | None = None,
        cluster_name: str | None = None,
    ) -> Sandbox:
        """Create a sandbox and wait for it to be running.

        Args:
            cpu: CPU allocation in cores (e.g. 1 = 1 vCPU). Must be a multiple of 0.25.
            memory_bytes: Memory allocation in bytes.
            snapshot_id: Optional snapshot ID to create the sandbox from.
            snapshot_alias: Optional snapshot alias to create the sandbox from.
            ttl: Optional seconds after creation before the sandbox is
                automatically terminated.
            tags: Optional key/value labels to attach to the sandbox.
            termination_policy: The termination snapshot policy, e.g.
                ``{"snapshot": {"memory": False, "aliases": ["prod"]}}``.
                Omit for an ephemeral sandbox (no snapshot, deleted on termination).
            cluster_name: Optional name of the cluster to launch the sandbox in.

        """
        body = CreateSandboxBody(
            snapshot_id=snapshot_id if snapshot_id is not None else UNSET,
            snapshot_alias=snapshot_alias if snapshot_alias is not None else UNSET,
            cpu=cpu,
            memory_bytes=memory_bytes,
            ttl=ttl if ttl is not None else UNSET,
            tags=CreateSandboxBodyTags.from_dict(tags) if tags is not None else UNSET,
            termination_policy=build_termination_policy(termination_policy),
            cluster_name=cluster_name if cluster_name is not None else UNSET,
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

    async def terminate(
        self,
        sandbox_id: str,
        *,
        snapshot: dict | None | Unset = UNSET,
    ) -> None:
        """Terminate a VM by sandbox ID.

        After this the sandbox is terminal and cannot be used again.

        Args:
            sandbox_id: The sandbox to terminate.
            snapshot: What this teardown snapshots, overriding the snapshot the
                sandbox's stored termination policy would take, e.g.
                ``{"memory": True}``. Omit (the default) to keep the stored
                policy; pass ``None`` to make the teardown ephemeral (no
                snapshot). The produced snapshot is aliased as
                ``sandbox:<sandbox id>`` plus any ``aliases``.
        """
        await _call_api(
            "api.terminate_sandbox",
            lambda: terminate_sandbox_api(
                sandbox_id,
                client=self._api_client,
                body=TerminateSandboxBody(
                    snapshot=build_termination_snapshot(snapshot),
                ),
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

        if vm_info.status != "terminated":
            raise RuntimeError(describe_lifecycle_failure(vm_info, "terminated"))

    async def hibernate(self, sandbox_id: str) -> None:
        """Hibernate (suspend) a VM — a terminate that snapshots filesystem and memory."""
        await self.terminate(sandbox_id, snapshot={"memory": True})

    async def shutdown(self, sandbox_id: str) -> None:
        """Shut down a VM — a terminate that snapshots the filesystem."""
        await self.terminate(sandbox_id, snapshot={"memory": False})

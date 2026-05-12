from __future__ import annotations


import os
from types import TracebackType

# ── Management API client ─────────────────────────────────────────────────────
from .api.client import AuthenticatedClient as ApiClient

from ._sandboxes import SandboxesNamespace
from ._snapshots import SnapshotsNamespace
from ._configuration import get_inferred_base_url
from ._utils import RetryConfig


class TogetherSandbox:
    """
    The main entry point for the Together Sandbox SDK.

    Provides a unified interface over both the management API (sandboxes,
    VMs, templates) and the in-VM Sandbox API (files, execs).

    Example::

        sdk = TogetherSandbox(api_key="your-key")
        async with await sdk.sandboxes.start("sandbox-id") as sb:
            await sb.files.read_file("/package.json")

    Args:
        api_key: Together AI API key. Falls back to ``TOGETHER_API_KEY`` env var.
        base_url: Management API base URL. Defaults to ``https://api.bartender.codesandbox.io``.
        retry: Optional retry configuration. When provided, all API calls will
            automatically retry on transient failures (HTTP 408/429/500/502/503/504
            and network errors). See :class:`~together_sandbox._utils.RetryConfig`.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        retry: RetryConfig | None = None,
    ) -> None:
        resolved_key = api_key or os.environ.get("TOGETHER_API_KEY")
        resolved_url = base_url or get_inferred_base_url()

        if not resolved_key:
            raise ValueError(
                "api_key must be provided or TOGETHER_API_KEY env var must be set"
            )
        self._api_key = resolved_key
        self._base_url = resolved_url + "/api/v1"
        self._retry = retry
        self._api_client = ApiClient(
            base_url=self._base_url,
            token=resolved_key,
            prefix="Bearer",
            # raise_on_unexpected_status is intentionally omitted (defaults to False).
            # _call_api owns all error handling and retry logic.
        )
        self.sandboxes = SandboxesNamespace(self._api_client, retry=retry)
        self.snapshots = SnapshotsNamespace(
            self._api_client, self._base_url, retry=retry, api_key=resolved_key
        )

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

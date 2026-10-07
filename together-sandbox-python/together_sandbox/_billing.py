from __future__ import annotations

from .api.client import AuthenticatedClient as ApiClient

# ── Management API endpoint functions (detailed variants) ─────────────────────
from .api.api.default.get_billing_usage import asyncio_detailed as get_billing_usage_api

# ── Management API models ─────────────────────────────────────────────────────
from .api.models.billing_usage_window import BillingUsageWindow
from .api.models.get_billing_usage_granularity import GetBillingUsageGranularity
from .api.types import UNSET

# ── Helpers ─────────────────────────────────────────────────────
from ._utils import RetryConfig, _call_api
from ._pagination import Page


class BillingNamespace:
    """Billing usage operations accessed as ``sdk.billing.*``."""

    def __init__(
        self,
        api_client: ApiClient,
        *,
        retry: RetryConfig | None = None,
    ) -> None:
        self._api_client = api_client
        self._retry = retry

    async def usage(
        self,
        *,
        month: str | None = None,
        granularity: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[BillingUsageWindow]:
        """Get the authenticated organization's billing usage for a single month.

        Returns a :class:`Page` of cost-annotated usage windows that is
        async-iterable across all pages — iterate it directly to walk every
        window, or use ``get_next_page()`` / ``next_cursor`` for manual
        page-by-page control.

        Usage data is cached: prior months refresh roughly every 24 hours,
        and the current month refreshes roughly hourly.

        Args:
            month: Billing month as ``YYYY-MM``. Defaults to the current
                month. Cannot be a future month or more than 12 months in the
                past.
            granularity: Time window size: ``"day"`` (default) or ``"hour"``.
            limit: Max time windows per page (1-1000, default 100).
            cursor: A ``next_cursor`` value returned by a previous page (omit
                to start from the first page). Only valid for the ``month``
                and ``granularity`` that produced it.

        Returns:
            Page[BillingUsageWindow]: First page of usage windows.

        Example:
            >>> async for window in await sdk.billing.usage(month="2026-06"):
            ...     for item in window.line_items:
            ...         print(item.product_name, item.cost)
        """

        async def fetch_page(cursor: str | None = None) -> Page[BillingUsageWindow]:
            result = await _call_api(
                "api.get_billing_usage",
                lambda: get_billing_usage_api(
                    client=self._api_client,
                    month=month if month is not None else UNSET,
                    granularity=(
                        GetBillingUsageGranularity(granularity)
                        if granularity is not None
                        else UNSET
                    ),
                    page_size=limit if limit is not None else UNSET,
                    page_token=cursor if cursor is not None else UNSET,
                ),
                self._retry,
            )
            return Page(result.data, result.next_page_token, fetch_page)

        return await fetch_page(cursor)

"""Unit tests for the BillingNamespace facade."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from together_sandbox._billing import BillingNamespace
from together_sandbox.api.models.billing_usage_line_item import BillingUsageLineItem
from together_sandbox.api.models.billing_usage_page import BillingUsagePage
from together_sandbox.api.models.billing_usage_page_currency import BillingUsagePageCurrency
from together_sandbox.api.models.billing_usage_page_object import BillingUsagePageObject
from together_sandbox.api.models.billing_usage_window import BillingUsageWindow
from together_sandbox.api.types import UNSET

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_line_item(**overrides) -> BillingUsageLineItem:
    defaults = dict(
        product_name="Token Based Inference (Per 1M Tokens)",
        quantity="1250.5",
        unit_price="0.20",
        cost="250.10",
        pricing_dimensions={"token_type": "input"},
        attributes={"api_key_id": "key_example", "project_id": "proj_example"},
    )
    defaults.update(overrides)
    return BillingUsageLineItem(**defaults)


def _make_window(**overrides) -> BillingUsageWindow:
    defaults = dict(
        date="2026-06-15",
        start_time="2026-06-15T00:00:00Z",
        end_time="2026-06-16T00:00:00Z",
        line_items=[_make_line_item()],
    )
    defaults.update(overrides)
    return BillingUsageWindow(**defaults)


def _make_usage_page(**overrides) -> BillingUsagePage:
    defaults = dict(
        object_=BillingUsagePageObject.BILLING_USAGE_REPORT,
        organization_id="org_example",
        billing_period="2026-06",
        earliest_window_start=None,
        latest_window_end=None,
        currency=BillingUsagePageCurrency.USD,
        data=[_make_window()],
        has_more=False,
        next_page_token=None,
    )
    defaults.update(overrides)
    return BillingUsagePage(**defaults)


# ─── BillingNamespace.usage ───────────────────────────────────────────────────


class TestBillingNamespaceUsage:
    @pytest.mark.asyncio
    async def test_passes_month_granularity_limit_and_cursor(self):
        with patch(
            "together_sandbox._billing.get_billing_usage_api",
            new=AsyncMock(),
        ) as mock_call:
            mock_call.return_value.parsed = _make_usage_page()
            mock_call.return_value.status_code = 200

            ns = BillingNamespace(api_client=object())
            await ns.usage(month="2026-06", granularity="hour", limit=50, cursor="cursor-1")

            mock_call.assert_called_once()
            kwargs = mock_call.call_args.kwargs
            assert kwargs["month"] == "2026-06"
            assert kwargs["granularity"].value == "hour"
            assert kwargs["page_size"] == 50
            assert kwargs["page_token"] == "cursor-1"

    @pytest.mark.asyncio
    async def test_leaves_params_unset_when_no_options_given(self):
        with patch(
            "together_sandbox._billing.get_billing_usage_api",
            new=AsyncMock(),
        ) as mock_call:
            mock_call.return_value.parsed = _make_usage_page()
            mock_call.return_value.status_code = 200

            ns = BillingNamespace(api_client=object())
            await ns.usage()

            kwargs = mock_call.call_args.kwargs
            assert kwargs["month"] is UNSET
            assert kwargs["granularity"] is UNSET
            assert kwargs["page_size"] is UNSET
            assert kwargs["page_token"] is UNSET

    @pytest.mark.asyncio
    async def test_returns_page_with_windows_and_cursor(self):
        page_model = _make_usage_page(has_more=True, next_page_token="next-token")
        with patch(
            "together_sandbox._billing.get_billing_usage_api",
            new=AsyncMock(),
        ) as mock_call:
            mock_call.return_value.parsed = page_model
            mock_call.return_value.status_code = 200

            ns = BillingNamespace(api_client=object())
            page = await ns.usage()

            assert page.data == page_model.data
            assert page.data[0].line_items[0].cost == "250.10"
            assert page.has_next_page() is True
            assert page.next_cursor == "next-token"

    @pytest.mark.asyncio
    async def test_fetches_next_page_using_previous_cursor(self):
        first_page = _make_usage_page(has_more=True, next_page_token="next-token")
        second_page = _make_usage_page(has_more=False)
        with patch(
            "together_sandbox._billing.get_billing_usage_api",
            new=AsyncMock(),
        ) as mock_call:
            mock_call.return_value.status_code = 200
            mock_call.side_effect = [
                type("R", (), {"parsed": first_page, "status_code": 200})(),
                type("R", (), {"parsed": second_page, "status_code": 200})(),
            ]

            ns = BillingNamespace(api_client=object())
            page = await ns.usage(month="2026-06")
            await page.get_next_page()

            second_call_kwargs = mock_call.call_args_list[1].kwargs
            assert second_call_kwargs["page_token"] == "next-token"

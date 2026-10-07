from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.billing_usage_page import BillingUsagePage
from ...models.error import Error
from ...models.get_billing_usage_granularity import GetBillingUsageGranularity
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    month: str | Unset = UNSET,
    granularity: GetBillingUsageGranularity | Unset = GetBillingUsageGranularity.DAY,
    page_size: int | Unset = 100,
    page_token: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["month"] = month

    json_granularity: str | Unset = UNSET
    if not isinstance(granularity, Unset):
        json_granularity = granularity.value

    params["granularity"] = json_granularity

    params["page_size"] = page_size

    params["page_token"] = page_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/billing/usage",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BillingUsagePage | Error | None:
    if response.status_code == 200:
        response_200 = BillingUsagePage.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[BillingUsagePage | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    month: str | Unset = UNSET,
    granularity: GetBillingUsageGranularity | Unset = GetBillingUsageGranularity.DAY,
    page_size: int | Unset = 100,
    page_token: str | Unset = UNSET,
) -> Response[BillingUsagePage | Error]:
    """Get billing usage

     Returns the authenticated organization's billing usage for a single month as flat, cost-annotated
    line items grouped into time windows. Usage is resolved from the Bearer API key's organization.

    Usage data is cached: prior months refresh roughly every 24 hours, and the current month refreshes
    roughly hourly (through the last completed hour at `hour` granularity, or through yesterday at `day`
    granularity).

    Args:
        month (str | Unset):
        granularity (GetBillingUsageGranularity | Unset):  Default:
            GetBillingUsageGranularity.DAY.
        page_size (int | Unset):  Default: 100.
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BillingUsagePage | Error]
    """

    kwargs = _get_kwargs(
        month=month,
        granularity=granularity,
        page_size=page_size,
        page_token=page_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    month: str | Unset = UNSET,
    granularity: GetBillingUsageGranularity | Unset = GetBillingUsageGranularity.DAY,
    page_size: int | Unset = 100,
    page_token: str | Unset = UNSET,
) -> BillingUsagePage | Error | None:
    """Get billing usage

     Returns the authenticated organization's billing usage for a single month as flat, cost-annotated
    line items grouped into time windows. Usage is resolved from the Bearer API key's organization.

    Usage data is cached: prior months refresh roughly every 24 hours, and the current month refreshes
    roughly hourly (through the last completed hour at `hour` granularity, or through yesterday at `day`
    granularity).

    Args:
        month (str | Unset):
        granularity (GetBillingUsageGranularity | Unset):  Default:
            GetBillingUsageGranularity.DAY.
        page_size (int | Unset):  Default: 100.
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BillingUsagePage | Error
    """

    return sync_detailed(
        client=client,
        month=month,
        granularity=granularity,
        page_size=page_size,
        page_token=page_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    month: str | Unset = UNSET,
    granularity: GetBillingUsageGranularity | Unset = GetBillingUsageGranularity.DAY,
    page_size: int | Unset = 100,
    page_token: str | Unset = UNSET,
) -> Response[BillingUsagePage | Error]:
    """Get billing usage

     Returns the authenticated organization's billing usage for a single month as flat, cost-annotated
    line items grouped into time windows. Usage is resolved from the Bearer API key's organization.

    Usage data is cached: prior months refresh roughly every 24 hours, and the current month refreshes
    roughly hourly (through the last completed hour at `hour` granularity, or through yesterday at `day`
    granularity).

    Args:
        month (str | Unset):
        granularity (GetBillingUsageGranularity | Unset):  Default:
            GetBillingUsageGranularity.DAY.
        page_size (int | Unset):  Default: 100.
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BillingUsagePage | Error]
    """

    kwargs = _get_kwargs(
        month=month,
        granularity=granularity,
        page_size=page_size,
        page_token=page_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    month: str | Unset = UNSET,
    granularity: GetBillingUsageGranularity | Unset = GetBillingUsageGranularity.DAY,
    page_size: int | Unset = 100,
    page_token: str | Unset = UNSET,
) -> BillingUsagePage | Error | None:
    """Get billing usage

     Returns the authenticated organization's billing usage for a single month as flat, cost-annotated
    line items grouped into time windows. Usage is resolved from the Bearer API key's organization.

    Usage data is cached: prior months refresh roughly every 24 hours, and the current month refreshes
    roughly hourly (through the last completed hour at `hour` granularity, or through yesterday at `day`
    granularity).

    Args:
        month (str | Unset):
        granularity (GetBillingUsageGranularity | Unset):  Default:
            GetBillingUsageGranularity.DAY.
        page_size (int | Unset):  Default: 100.
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BillingUsagePage | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            month=month,
            granularity=granularity,
            page_size=page_size,
            page_token=page_token,
        )
    ).parsed

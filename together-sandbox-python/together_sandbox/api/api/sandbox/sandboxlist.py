from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.sandbox_list_response import SandboxListResponse
from ...models.sandboxlist_direction import SandboxlistDirection
from ...models.sandboxlist_order_by import SandboxlistOrderBy
from ...models.sandboxlist_status import SandboxlistStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    tags: str | Unset = UNSET,
    order_by: SandboxlistOrderBy | Unset = SandboxlistOrderBy.UPDATED_AT,
    direction: SandboxlistDirection | Unset = SandboxlistDirection.DESC,
    page_size: int | Unset = 20,
    page: int | Unset = 1,
    status: SandboxlistStatus | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["tags"] = tags

    json_order_by: str | Unset = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["order_by"] = json_order_by

    json_direction: str | Unset = UNSET
    if not isinstance(direction, Unset):
        json_direction = direction.value

    params["direction"] = json_direction

    params["page_size"] = page_size

    params["page"] = page

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sandbox",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SandboxListResponse | None:
    if response.status_code == 200:
        response_200 = SandboxListResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SandboxListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    tags: str | Unset = UNSET,
    order_by: SandboxlistOrderBy | Unset = SandboxlistOrderBy.UPDATED_AT,
    direction: SandboxlistDirection | Unset = SandboxlistDirection.DESC,
    page_size: int | Unset = 20,
    page: int | Unset = 1,
    status: SandboxlistStatus | Unset = UNSET,
) -> Response[SandboxListResponse]:
    """List Sandboxes

     List sandboxes from the current workspace with optional filters.
    Results are limited to a maximum of 50 sandboxes per request.

    Args:
        tags (str | Unset):
        order_by (SandboxlistOrderBy | Unset):  Default: SandboxlistOrderBy.UPDATED_AT.
        direction (SandboxlistDirection | Unset):  Default: SandboxlistDirection.DESC.
        page_size (int | Unset):  Default: 20.
        page (int | Unset):  Default: 1.
        status (SandboxlistStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SandboxListResponse]
    """

    kwargs = _get_kwargs(
        tags=tags,
        order_by=order_by,
        direction=direction,
        page_size=page_size,
        page=page,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    tags: str | Unset = UNSET,
    order_by: SandboxlistOrderBy | Unset = SandboxlistOrderBy.UPDATED_AT,
    direction: SandboxlistDirection | Unset = SandboxlistDirection.DESC,
    page_size: int | Unset = 20,
    page: int | Unset = 1,
    status: SandboxlistStatus | Unset = UNSET,
) -> SandboxListResponse | None:
    """List Sandboxes

     List sandboxes from the current workspace with optional filters.
    Results are limited to a maximum of 50 sandboxes per request.

    Args:
        tags (str | Unset):
        order_by (SandboxlistOrderBy | Unset):  Default: SandboxlistOrderBy.UPDATED_AT.
        direction (SandboxlistDirection | Unset):  Default: SandboxlistDirection.DESC.
        page_size (int | Unset):  Default: 20.
        page (int | Unset):  Default: 1.
        status (SandboxlistStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SandboxListResponse
    """

    return sync_detailed(
        client=client,
        tags=tags,
        order_by=order_by,
        direction=direction,
        page_size=page_size,
        page=page,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    tags: str | Unset = UNSET,
    order_by: SandboxlistOrderBy | Unset = SandboxlistOrderBy.UPDATED_AT,
    direction: SandboxlistDirection | Unset = SandboxlistDirection.DESC,
    page_size: int | Unset = 20,
    page: int | Unset = 1,
    status: SandboxlistStatus | Unset = UNSET,
) -> Response[SandboxListResponse]:
    """List Sandboxes

     List sandboxes from the current workspace with optional filters.
    Results are limited to a maximum of 50 sandboxes per request.

    Args:
        tags (str | Unset):
        order_by (SandboxlistOrderBy | Unset):  Default: SandboxlistOrderBy.UPDATED_AT.
        direction (SandboxlistDirection | Unset):  Default: SandboxlistDirection.DESC.
        page_size (int | Unset):  Default: 20.
        page (int | Unset):  Default: 1.
        status (SandboxlistStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SandboxListResponse]
    """

    kwargs = _get_kwargs(
        tags=tags,
        order_by=order_by,
        direction=direction,
        page_size=page_size,
        page=page,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    tags: str | Unset = UNSET,
    order_by: SandboxlistOrderBy | Unset = SandboxlistOrderBy.UPDATED_AT,
    direction: SandboxlistDirection | Unset = SandboxlistDirection.DESC,
    page_size: int | Unset = 20,
    page: int | Unset = 1,
    status: SandboxlistStatus | Unset = UNSET,
) -> SandboxListResponse | None:
    """List Sandboxes

     List sandboxes from the current workspace with optional filters.
    Results are limited to a maximum of 50 sandboxes per request.

    Args:
        tags (str | Unset):
        order_by (SandboxlistOrderBy | Unset):  Default: SandboxlistOrderBy.UPDATED_AT.
        direction (SandboxlistDirection | Unset):  Default: SandboxlistDirection.DESC.
        page_size (int | Unset):  Default: 20.
        page (int | Unset):  Default: 1.
        status (SandboxlistStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SandboxListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            tags=tags,
            order_by=order_by,
            direction=direction,
            page_size=page_size,
            page=page,
            status=status,
        )
    ).parsed

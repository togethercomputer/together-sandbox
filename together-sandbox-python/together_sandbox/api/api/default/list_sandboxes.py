from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_sandboxes_statuses_item import ListSandboxesStatusesItem
from ...models.sandbox_page import SandboxPage
from ...models.tags import Tags
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: int | Unset = 20,
    cursor: str | Unset = UNSET,
    statuses: list[ListSandboxesStatusesItem] | Unset = UNSET,
    tags: Tags | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["cursor"] = cursor

    json_statuses: list[str] | Unset = UNSET
    if not isinstance(statuses, Unset):
        json_statuses = []
        for statuses_item_data in statuses:
            statuses_item = statuses_item_data.value
            json_statuses.append(statuses_item)

    params["statuses[]"] = json_statuses

    json_tags: dict[str, Any] | Unset = UNSET
    if not isinstance(tags, Unset):
        json_tags = tags.to_dict()
    if not isinstance(json_tags, Unset):
        params.update(json_tags)

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sandboxes",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | SandboxPage | None:
    if response.status_code == 200:
        response_200 = SandboxPage.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | SandboxPage]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    cursor: str | Unset = UNSET,
    statuses: list[ListSandboxesStatusesItem] | Unset = UNSET,
    tags: Tags | Unset = UNSET,
) -> Response[Error | SandboxPage]:
    """List sandboxes

    Args:
        limit (int | Unset):  Default: 20.
        cursor (str | Unset):
        statuses (list[ListSandboxesStatusesItem] | Unset):
        tags (Tags | Unset): User-defined key-value labels (both keys and values are strings).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | SandboxPage]
    """

    kwargs = _get_kwargs(
        limit=limit,
        cursor=cursor,
        statuses=statuses,
        tags=tags,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    cursor: str | Unset = UNSET,
    statuses: list[ListSandboxesStatusesItem] | Unset = UNSET,
    tags: Tags | Unset = UNSET,
) -> Error | SandboxPage | None:
    """List sandboxes

    Args:
        limit (int | Unset):  Default: 20.
        cursor (str | Unset):
        statuses (list[ListSandboxesStatusesItem] | Unset):
        tags (Tags | Unset): User-defined key-value labels (both keys and values are strings).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | SandboxPage
    """

    return sync_detailed(
        client=client,
        limit=limit,
        cursor=cursor,
        statuses=statuses,
        tags=tags,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    cursor: str | Unset = UNSET,
    statuses: list[ListSandboxesStatusesItem] | Unset = UNSET,
    tags: Tags | Unset = UNSET,
) -> Response[Error | SandboxPage]:
    """List sandboxes

    Args:
        limit (int | Unset):  Default: 20.
        cursor (str | Unset):
        statuses (list[ListSandboxesStatusesItem] | Unset):
        tags (Tags | Unset): User-defined key-value labels (both keys and values are strings).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | SandboxPage]
    """

    kwargs = _get_kwargs(
        limit=limit,
        cursor=cursor,
        statuses=statuses,
        tags=tags,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    cursor: str | Unset = UNSET,
    statuses: list[ListSandboxesStatusesItem] | Unset = UNSET,
    tags: Tags | Unset = UNSET,
) -> Error | SandboxPage | None:
    """List sandboxes

    Args:
        limit (int | Unset):  Default: 20.
        cursor (str | Unset):
        statuses (list[ListSandboxesStatusesItem] | Unset):
        tags (Tags | Unset): User-defined key-value labels (both keys and values are strings).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | SandboxPage
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            cursor=cursor,
            statuses=statuses,
            tags=tags,
        )
    ).parsed

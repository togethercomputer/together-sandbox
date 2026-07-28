from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.watcher_event import WatcherEvent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    path: str,
    *,
    recursive: bool | Unset = UNSET,
    ignore_patterns: list[str] | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["recursive"] = recursive

    json_ignore_patterns: list[str] | Unset = UNSET
    if not isinstance(ignore_patterns, Unset):
        json_ignore_patterns = ignore_patterns

    params["ignorePatterns"] = json_ignore_patterns

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/stream/directories/watcher/{path}".format(
            path=quote(str(path), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | WatcherEvent:
    if response.status_code == 200:
        response_200 = WatcherEvent.from_dict(response.text)

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    response_default = Error.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | WatcherEvent]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    path: str,
    *,
    client: AuthenticatedClient,
    recursive: bool | Unset = UNSET,
    ignore_patterns: list[str] | Unset = UNSET,
) -> Response[Error | WatcherEvent]:
    """Watch directory changes using Server-Sent Events (SSE)

     Watch a directory for file system changes and stream events via SSE.

    Args:
        path (str):
        recursive (bool | Unset):
        ignore_patterns (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | WatcherEvent]
    """

    kwargs = _get_kwargs(
        path=path,
        recursive=recursive,
        ignore_patterns=ignore_patterns,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    path: str,
    *,
    client: AuthenticatedClient,
    recursive: bool | Unset = UNSET,
    ignore_patterns: list[str] | Unset = UNSET,
) -> Error | WatcherEvent | None:
    """Watch directory changes using Server-Sent Events (SSE)

     Watch a directory for file system changes and stream events via SSE.

    Args:
        path (str):
        recursive (bool | Unset):
        ignore_patterns (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | WatcherEvent
    """

    return sync_detailed(
        path=path,
        client=client,
        recursive=recursive,
        ignore_patterns=ignore_patterns,
    ).parsed


async def asyncio_detailed(
    path: str,
    *,
    client: AuthenticatedClient,
    recursive: bool | Unset = UNSET,
    ignore_patterns: list[str] | Unset = UNSET,
) -> Response[Error | WatcherEvent]:
    """Watch directory changes using Server-Sent Events (SSE)

     Watch a directory for file system changes and stream events via SSE.

    Args:
        path (str):
        recursive (bool | Unset):
        ignore_patterns (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | WatcherEvent]
    """

    kwargs = _get_kwargs(
        path=path,
        recursive=recursive,
        ignore_patterns=ignore_patterns,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    path: str,
    *,
    client: AuthenticatedClient,
    recursive: bool | Unset = UNSET,
    ignore_patterns: list[str] | Unset = UNSET,
) -> Error | WatcherEvent | None:
    """Watch directory changes using Server-Sent Events (SSE)

     Watch a directory for file system changes and stream events via SSE.

    Args:
        path (str):
        recursive (bool | Unset):
        ignore_patterns (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | WatcherEvent
    """

    return (
        await asyncio_detailed(
            path=path,
            client=client,
            recursive=recursive,
            ignore_patterns=ignore_patterns,
        )
    ).parsed

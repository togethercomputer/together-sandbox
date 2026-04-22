from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.snapshot import Snapshot
from ...types import Response


def _get_kwargs(
    alias: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/snapshots/@{alias}".format(
            alias=quote(str(alias), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | Snapshot | None:
    if response.status_code == 200:
        response_200 = Snapshot.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | Snapshot]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    alias: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | Snapshot]:
    """Get a snapshot by alias

    Args:
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Snapshot]
    """

    kwargs = _get_kwargs(
        alias=alias,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    alias: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | Snapshot | None:
    """Get a snapshot by alias

    Args:
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Snapshot
    """

    return sync_detailed(
        alias=alias,
        client=client,
    ).parsed


async def asyncio_detailed(
    alias: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | Snapshot]:
    """Get a snapshot by alias

    Args:
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | Snapshot]
    """

    kwargs = _get_kwargs(
        alias=alias,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    alias: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | Snapshot | None:
    """Get a snapshot by alias

    Args:
        alias (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | Snapshot
    """

    return (
        await asyncio_detailed(
            alias=alias,
            client=client,
        )
    ).parsed

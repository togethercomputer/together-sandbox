from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.snapshot_alias import SnapshotAlias
from ...types import Response


def _get_kwargs(
    snapshot_id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/snapshots/{snapshot_id}/aliases".format(
            snapshot_id=quote(str(snapshot_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | list[SnapshotAlias] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SnapshotAlias.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | list[SnapshotAlias]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    snapshot_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[SnapshotAlias]]:
    """List a snapshot's aliases

    Args:
        snapshot_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[SnapshotAlias]]
    """

    kwargs = _get_kwargs(
        snapshot_id=snapshot_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    snapshot_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[SnapshotAlias] | None:
    """List a snapshot's aliases

    Args:
        snapshot_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[SnapshotAlias]
    """

    return sync_detailed(
        snapshot_id=snapshot_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    snapshot_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[SnapshotAlias]]:
    """List a snapshot's aliases

    Args:
        snapshot_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[SnapshotAlias]]
    """

    kwargs = _get_kwargs(
        snapshot_id=snapshot_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    snapshot_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[SnapshotAlias] | None:
    """List a snapshot's aliases

    Args:
        snapshot_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[SnapshotAlias]
    """

    return (
        await asyncio_detailed(
            snapshot_id=snapshot_id,
            client=client,
        )
    ).parsed

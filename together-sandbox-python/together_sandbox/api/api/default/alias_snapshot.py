from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.alias_snapshot_body import AliasSnapshotBody
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    snapshot_id: UUID,
    *,
    body: AliasSnapshotBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/snapshots/{snapshot_id}/aliases".format(
            snapshot_id=quote(str(snapshot_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

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
) -> Response[Any | Error]:
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
    body: AliasSnapshotBody,
) -> Response[Any | Error]:
    """Assign an alias to a snapshot

    Args:
        snapshot_id (UUID):
        body (AliasSnapshotBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        snapshot_id=snapshot_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    snapshot_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: AliasSnapshotBody,
) -> Any | Error | None:
    """Assign an alias to a snapshot

    Args:
        snapshot_id (UUID):
        body (AliasSnapshotBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        snapshot_id=snapshot_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    snapshot_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: AliasSnapshotBody,
) -> Response[Any | Error]:
    """Assign an alias to a snapshot

    Args:
        snapshot_id (UUID):
        body (AliasSnapshotBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        snapshot_id=snapshot_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    snapshot_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: AliasSnapshotBody,
) -> Any | Error | None:
    """Assign an alias to a snapshot

    Args:
        snapshot_id (UUID):
        body (AliasSnapshotBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            snapshot_id=snapshot_id,
            client=client,
            body=body,
        )
    ).parsed

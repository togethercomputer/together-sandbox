from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.preview_token_update_request import PreviewTokenUpdateRequest
from ...models.preview_token_update_response import PreviewTokenUpdateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    token_id: str,
    *,
    body: PreviewTokenUpdateRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/sandbox/{id}/tokens/{token_id}".format(
            id=quote(str(id), safe=""),
            token_id=quote(str(token_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PreviewTokenUpdateResponse | None:
    if response.status_code == 201:
        response_201 = PreviewTokenUpdateResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PreviewTokenUpdateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: PreviewTokenUpdateRequest | Unset = UNSET,
) -> Response[PreviewTokenUpdateResponse]:
    """Update a Preview Token

     Update a Preview token that allow access to a private sandbox

    Args:
        id (str):
        token_id (str):
        body (PreviewTokenUpdateRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PreviewTokenUpdateResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        token_id=token_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: PreviewTokenUpdateRequest | Unset = UNSET,
) -> PreviewTokenUpdateResponse | None:
    """Update a Preview Token

     Update a Preview token that allow access to a private sandbox

    Args:
        id (str):
        token_id (str):
        body (PreviewTokenUpdateRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PreviewTokenUpdateResponse
    """

    return sync_detailed(
        id=id,
        token_id=token_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: PreviewTokenUpdateRequest | Unset = UNSET,
) -> Response[PreviewTokenUpdateResponse]:
    """Update a Preview Token

     Update a Preview token that allow access to a private sandbox

    Args:
        id (str):
        token_id (str):
        body (PreviewTokenUpdateRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PreviewTokenUpdateResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        token_id=token_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: PreviewTokenUpdateRequest | Unset = UNSET,
) -> PreviewTokenUpdateResponse | None:
    """Update a Preview Token

     Update a Preview token that allow access to a private sandbox

    Args:
        id (str):
        token_id (str):
        body (PreviewTokenUpdateRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PreviewTokenUpdateResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            token_id=token_id,
            client=client,
            body=body,
        )
    ).parsed

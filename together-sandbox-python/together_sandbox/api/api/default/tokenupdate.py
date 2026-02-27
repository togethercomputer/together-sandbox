from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.token_update_request import TokenUpdateRequest
from ...models.token_update_response import TokenUpdateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_id: str,
    token_id: str,
    *,
    body: TokenUpdateRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/org/workspace/{team_id}/tokens/{token_id}".format(
            team_id=quote(str(team_id), safe=""),
            token_id=quote(str(token_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> TokenUpdateResponse | None:
    if response.status_code == 201:
        response_201 = TokenUpdateResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[TokenUpdateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: TokenUpdateRequest | Unset = UNSET,
) -> Response[TokenUpdateResponse]:
    """Update an API Token

     Update an API token for a workspace that is part of the current organization.

    Args:
        team_id (str):
        token_id (str):
        body (TokenUpdateRequest | Unset): Updateable fields for API Tokens. Omitting a field will
            not update it; explicitly passing null or an empty list will clear the value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TokenUpdateResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        token_id=token_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: TokenUpdateRequest | Unset = UNSET,
) -> TokenUpdateResponse | None:
    """Update an API Token

     Update an API token for a workspace that is part of the current organization.

    Args:
        team_id (str):
        token_id (str):
        body (TokenUpdateRequest | Unset): Updateable fields for API Tokens. Omitting a field will
            not update it; explicitly passing null or an empty list will clear the value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TokenUpdateResponse
    """

    return sync_detailed(
        team_id=team_id,
        token_id=token_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: TokenUpdateRequest | Unset = UNSET,
) -> Response[TokenUpdateResponse]:
    """Update an API Token

     Update an API token for a workspace that is part of the current organization.

    Args:
        team_id (str):
        token_id (str):
        body (TokenUpdateRequest | Unset): Updateable fields for API Tokens. Omitting a field will
            not update it; explicitly passing null or an empty list will clear the value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TokenUpdateResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        token_id=token_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: TokenUpdateRequest | Unset = UNSET,
) -> TokenUpdateResponse | None:
    """Update an API Token

     Update an API token for a workspace that is part of the current organization.

    Args:
        team_id (str):
        token_id (str):
        body (TokenUpdateRequest | Unset): Updateable fields for API Tokens. Omitting a field will
            not update it; explicitly passing null or an empty list will clear the value.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TokenUpdateResponse
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            token_id=token_id,
            client=client,
            body=body,
        )
    ).parsed

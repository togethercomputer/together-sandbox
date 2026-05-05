from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.exec_stdout import ExecStdout
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    last_sequence: int | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["lastSequence"] = last_sequence

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/execs/{id}/io".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | list[ExecStdout]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ExecStdout.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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

    response_default = Error.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | list[ExecStdout]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    last_sequence: int | Unset = UNSET,
) -> Response[Error | list[ExecStdout]]:
    """Get exec output

     Retrieves the plain text output from an exec's buffer

    Args:
        id (str):
        last_sequence (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[ExecStdout]]
    """

    kwargs = _get_kwargs(
        id=id,
        last_sequence=last_sequence,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    last_sequence: int | Unset = UNSET,
) -> Error | list[ExecStdout] | None:
    """Get exec output

     Retrieves the plain text output from an exec's buffer

    Args:
        id (str):
        last_sequence (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[ExecStdout]
    """

    return sync_detailed(
        id=id,
        client=client,
        last_sequence=last_sequence,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    last_sequence: int | Unset = UNSET,
) -> Response[Error | list[ExecStdout]]:
    """Get exec output

     Retrieves the plain text output from an exec's buffer

    Args:
        id (str):
        last_sequence (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[ExecStdout]]
    """

    kwargs = _get_kwargs(
        id=id,
        last_sequence=last_sequence,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    last_sequence: int | Unset = UNSET,
) -> Error | list[ExecStdout] | None:
    """Get exec output

     Retrieves the plain text output from an exec's buffer

    Args:
        id (str):
        last_sequence (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[ExecStdout]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            last_sequence=last_sequence,
        )
    ).parsed

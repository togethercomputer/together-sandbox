from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.vm_create_session_request import VMCreateSessionRequest
from ...models.vm_create_session_response import VMCreateSessionResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    body: VMCreateSessionRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/vm/{id}/sessions".format(
            id=quote(str(id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VMCreateSessionResponse | None:
    if response.status_code == 200:
        response_200 = VMCreateSessionResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[VMCreateSessionResponse]:
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
    body: VMCreateSessionRequest | Unset = UNSET,
) -> Response[VMCreateSessionResponse]:
    """Create a new session on a VM

     Creates a new session on a running VM. A session represents an isolated Linux user, with their own
    container.
    A session has a single use token that the user can use to connect to the VM. This token has specific
    permissions (currently, read or write).
    The session is identified by a unique session ID, and the Linux username is based on the session ID.

    The Git user name and email can be configured via parameters.

    This endpoint requires the VM to be running. If the VM is not running, it will return a 404 error.

    Args:
        id (str):
        body (VMCreateSessionRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMCreateSessionResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    body: VMCreateSessionRequest | Unset = UNSET,
) -> VMCreateSessionResponse | None:
    """Create a new session on a VM

     Creates a new session on a running VM. A session represents an isolated Linux user, with their own
    container.
    A session has a single use token that the user can use to connect to the VM. This token has specific
    permissions (currently, read or write).
    The session is identified by a unique session ID, and the Linux username is based on the session ID.

    The Git user name and email can be configured via parameters.

    This endpoint requires the VM to be running. If the VM is not running, it will return a 404 error.

    Args:
        id (str):
        body (VMCreateSessionRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMCreateSessionResponse
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: VMCreateSessionRequest | Unset = UNSET,
) -> Response[VMCreateSessionResponse]:
    """Create a new session on a VM

     Creates a new session on a running VM. A session represents an isolated Linux user, with their own
    container.
    A session has a single use token that the user can use to connect to the VM. This token has specific
    permissions (currently, read or write).
    The session is identified by a unique session ID, and the Linux username is based on the session ID.

    The Git user name and email can be configured via parameters.

    This endpoint requires the VM to be running. If the VM is not running, it will return a 404 error.

    Args:
        id (str):
        body (VMCreateSessionRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMCreateSessionResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    body: VMCreateSessionRequest | Unset = UNSET,
) -> VMCreateSessionResponse | None:
    """Create a new session on a VM

     Creates a new session on a running VM. A session represents an isolated Linux user, with their own
    container.
    A session has a single use token that the user can use to connect to the VM. This token has specific
    permissions (currently, read or write).
    The session is identified by a unique session ID, and the Linux username is based on the session ID.

    The Git user name and email can be configured via parameters.

    This endpoint requires the VM to be running. If the VM is not running, it will return a 404 error.

    Args:
        id (str):
        body (VMCreateSessionRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMCreateSessionResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed

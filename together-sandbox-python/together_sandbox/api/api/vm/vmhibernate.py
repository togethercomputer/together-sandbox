from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.vm_hibernate_response import VMHibernateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    body: Any | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/vm/{id}/hibernate".format(
            id=quote(str(id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> VMHibernateResponse | None:
    if response.status_code == 200:
        response_200 = VMHibernateResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[VMHibernateResponse]:
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
    body: Any | Unset = UNSET,
) -> Response[VMHibernateResponse]:
    """Hibernate a VM

     Suspends a running VM, saving a snapshot of its memory and running processes

    This endpoint may take an extended amount of time to return (30 seconds). If the VM is not
    currently running, it will return an error (404).

    Unless later shut down by request or due to inactivity, a hibernated VM can be resumed with
    minimal latency.

    Args:
        id (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMHibernateResponse]
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
    body: Any | Unset = UNSET,
) -> VMHibernateResponse | None:
    """Hibernate a VM

     Suspends a running VM, saving a snapshot of its memory and running processes

    This endpoint may take an extended amount of time to return (30 seconds). If the VM is not
    currently running, it will return an error (404).

    Unless later shut down by request or due to inactivity, a hibernated VM can be resumed with
    minimal latency.

    Args:
        id (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMHibernateResponse
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
    body: Any | Unset = UNSET,
) -> Response[VMHibernateResponse]:
    """Hibernate a VM

     Suspends a running VM, saving a snapshot of its memory and running processes

    This endpoint may take an extended amount of time to return (30 seconds). If the VM is not
    currently running, it will return an error (404).

    Unless later shut down by request or due to inactivity, a hibernated VM can be resumed with
    minimal latency.

    Args:
        id (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMHibernateResponse]
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
    body: Any | Unset = UNSET,
) -> VMHibernateResponse | None:
    """Hibernate a VM

     Suspends a running VM, saving a snapshot of its memory and running processes

    This endpoint may take an extended amount of time to return (30 seconds). If the VM is not
    currently running, it will return an error (404).

    Unless later shut down by request or due to inactivity, a hibernated VM can be resumed with
    minimal latency.

    Args:
        id (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMHibernateResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed

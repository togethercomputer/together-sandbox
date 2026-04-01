from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.vm_list_running_v_ms_response import VMListRunningVMsResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/vm/running",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VMListRunningVMsResponse | None:
    if response.status_code == 200:
        response_200 = VMListRunningVMsResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[VMListRunningVMsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[VMListRunningVMsResponse]:
    """List information about currently running VMs

     List information about currently running VMs. This information is updated roughly every 30 seconds,
    so this data is not guaranteed to be perfectly up-to-date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMListRunningVMsResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> VMListRunningVMsResponse | None:
    """List information about currently running VMs

     List information about currently running VMs. This information is updated roughly every 30 seconds,
    so this data is not guaranteed to be perfectly up-to-date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMListRunningVMsResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[VMListRunningVMsResponse]:
    """List information about currently running VMs

     List information about currently running VMs. This information is updated roughly every 30 seconds,
    so this data is not guaranteed to be perfectly up-to-date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMListRunningVMsResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> VMListRunningVMsResponse | None:
    """List information about currently running VMs

     List information about currently running VMs. This information is updated roughly every 30 seconds,
    so this data is not guaranteed to be perfectly up-to-date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMListRunningVMsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

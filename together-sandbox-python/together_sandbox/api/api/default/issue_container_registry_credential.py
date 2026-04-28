from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.container_registry_credential import ContainerRegistryCredential
from ...models.error import Error
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/container-registries/default/credentials",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContainerRegistryCredential | Error | None:
    if response.status_code == 201:
        response_201 = ContainerRegistryCredential.from_dict(response.json())

        return response_201

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ContainerRegistryCredential | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ContainerRegistryCredential | Error]:
    """Issue a container registry credential for the authenticated user

     Returns credentials (username, password, registry URL) for authenticating with the container
    registry. The registry URL includes the user's namespace path derived from their project ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContainerRegistryCredential | Error]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> ContainerRegistryCredential | Error | None:
    """Issue a container registry credential for the authenticated user

     Returns credentials (username, password, registry URL) for authenticating with the container
    registry. The registry URL includes the user's namespace path derived from their project ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContainerRegistryCredential | Error
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ContainerRegistryCredential | Error]:
    """Issue a container registry credential for the authenticated user

     Returns credentials (username, password, registry URL) for authenticating with the container
    registry. The registry URL includes the user's namespace path derived from their project ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContainerRegistryCredential | Error]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> ContainerRegistryCredential | Error | None:
    """Issue a container registry credential for the authenticated user

     Returns credentials (username, password, registry URL) for authenticating with the container
    registry. The registry URL includes the user's namespace path derived from their project ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContainerRegistryCredential | Error
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

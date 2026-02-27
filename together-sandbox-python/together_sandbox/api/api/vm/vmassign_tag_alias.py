from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.vm_assign_tag_alias_request import VMAssignTagAliasRequest
from ...models.vm_assign_tag_alias_response import VMAssignTagAliasResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    namespace: str,
    alias: str,
    *,
    body: VMAssignTagAliasRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/vm/alias/{namespace}/{alias}".format(
            namespace=quote(str(namespace), safe=""),
            alias=quote(str(alias), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VMAssignTagAliasResponse | None:
    if response.status_code == 200:
        response_200 = VMAssignTagAliasResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[VMAssignTagAliasResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    namespace: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    body: VMAssignTagAliasRequest | Unset = UNSET,
) -> Response[VMAssignTagAliasResponse]:
    """Assign a tag alias to a VM tag

     Assign a tag alias to a VM tag.

    Args:
        namespace (str):
        alias (str):
        body (VMAssignTagAliasRequest | Unset): Assign a tag alias to a VM

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMAssignTagAliasResponse]
    """

    kwargs = _get_kwargs(
        namespace=namespace,
        alias=alias,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    namespace: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    body: VMAssignTagAliasRequest | Unset = UNSET,
) -> VMAssignTagAliasResponse | None:
    """Assign a tag alias to a VM tag

     Assign a tag alias to a VM tag.

    Args:
        namespace (str):
        alias (str):
        body (VMAssignTagAliasRequest | Unset): Assign a tag alias to a VM

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMAssignTagAliasResponse
    """

    return sync_detailed(
        namespace=namespace,
        alias=alias,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    namespace: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    body: VMAssignTagAliasRequest | Unset = UNSET,
) -> Response[VMAssignTagAliasResponse]:
    """Assign a tag alias to a VM tag

     Assign a tag alias to a VM tag.

    Args:
        namespace (str):
        alias (str):
        body (VMAssignTagAliasRequest | Unset): Assign a tag alias to a VM

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VMAssignTagAliasResponse]
    """

    kwargs = _get_kwargs(
        namespace=namespace,
        alias=alias,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    namespace: str,
    alias: str,
    *,
    client: AuthenticatedClient,
    body: VMAssignTagAliasRequest | Unset = UNSET,
) -> VMAssignTagAliasResponse | None:
    """Assign a tag alias to a VM tag

     Assign a tag alias to a VM tag.

    Args:
        namespace (str):
        alias (str):
        body (VMAssignTagAliasRequest | Unset): Assign a tag alias to a VM

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VMAssignTagAliasResponse
    """

    return (
        await asyncio_detailed(
            namespace=namespace,
            alias=alias,
            client=client,
            body=body,
        )
    ).parsed

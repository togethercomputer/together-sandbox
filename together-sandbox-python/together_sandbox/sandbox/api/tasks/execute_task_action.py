from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.task_action_response import TaskActionResponse
from ...models.task_action_type import TaskActionType
from ...types import UNSET, Response


def _get_kwargs(
    id: str,
    *,
    action_type: TaskActionType,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_action_type = action_type.value
    params["actionType"] = json_action_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/v1/tasks/{id}/actions".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | TaskActionResponse:
    if response.status_code == 200:
        response_200 = TaskActionResponse.from_dict(response.json())

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

    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())

        return response_409

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    response_default = Error.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | TaskActionResponse]:
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
    action_type: TaskActionType,
) -> Response[Error | TaskActionResponse]:
    """Execute task action

     Executes an action on a specific task (start, stop, or restart).

    Args:
        id (str):
        action_type (TaskActionType): Type of action to execute on a task

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | TaskActionResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        action_type=action_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    action_type: TaskActionType,
) -> Error | TaskActionResponse | None:
    """Execute task action

     Executes an action on a specific task (start, stop, or restart).

    Args:
        id (str):
        action_type (TaskActionType): Type of action to execute on a task

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | TaskActionResponse
    """

    return sync_detailed(
        id=id,
        client=client,
        action_type=action_type,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    action_type: TaskActionType,
) -> Response[Error | TaskActionResponse]:
    """Execute task action

     Executes an action on a specific task (start, stop, or restart).

    Args:
        id (str):
        action_type (TaskActionType): Type of action to execute on a task

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | TaskActionResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        action_type=action_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    action_type: TaskActionType,
) -> Error | TaskActionResponse | None:
    """Execute task action

     Executes an action on a specific task (start, stop, or restart).

    Args:
        id (str):
        action_type (TaskActionType): Type of action to execute on a task

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | TaskActionResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            action_type=action_type,
        )
    ).parsed

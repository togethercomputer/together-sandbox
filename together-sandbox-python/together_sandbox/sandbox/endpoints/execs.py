from typing import Any, AsyncIterator, Callable, Dict, NoReturn, Optional, Protocol, cast, runtime_checkable

from ..models.create_exec_request import CreateExecRequest
from ..models.error import Error
from ..models.exec_delete_response import ExecDeleteResponse
from ..models.exec_item import ExecItem
from ..models.exec_list_response import ExecListResponse
from ..models.exec_stdin import ExecStdin
from ..models.update_exec_request import UpdateExecRequest
from together_sandbox.core import BadRequestError, ConflictError, Error101, InternalServerError, NotFoundError, UnauthorisedError
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_bytes, iter_sse_events_text
from together_sandbox.core.utils import DataclassSerializer

import collections.abc
import json

from ..models.create_exec_request import CreateExecRequest
from ..models.error import Error
from ..models.exec_delete_response import ExecDeleteResponse
from ..models.exec_item import ExecItem
from ..models.exec_list_response import ExecListResponse
from ..models.exec_stdin import ExecStdin
from ..models.update_exec_request import UpdateExecRequest

@runtime_checkable
class ExecsClientProtocol(Protocol):
    """Protocol defining the interface of ExecsClient for dependency injection."""
    
    async def create_exec(
    self,
    body: CreateExecRequest,
    ) -> ExecItem: ...
    
    async def list_execs(
    self,
    ) -> ExecListResponse: ...
    
    async def get_exec(
    self,
    id_: str,
    ) -> ExecItem: ...
    
    async def update_exec(
    self,
    id_: str,
    body: UpdateExecRequest,
    ) -> ExecItem: ...
    
    async def delete_exec(
    self,
    id_: str,
    ) -> ExecDeleteResponse: ...
    
    def get_exec_output(
    self,
    id_: str,
    last_sequence: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]: ...
    
    async def exec_exec_stdin(
    self,
    id_: str,
    body: ExecStdin,
    ) -> ExecItem: ...
    
    async def connect_to_exec_web_socket(
    self,
    id_: str,
    ) -> Error: ...
    
    def stream_execs_list(
    self,
    ) -> AsyncIterator[dict[str, Any]]: ...
    


class ExecsClient(ExecsClientProtocol):
    """Client for execs endpoints. Uses HttpTransport for all HTTP and header management."""
    
    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url
    
    async def create_exec(
        self,
        body: CreateExecRequest,
    ) -> ExecItem:
        """
        Create a new exec
        
        Creates a new exec with specified command and arguments.
        
        Args:
            body (CreateExecRequest) : Exec creation request (json)
        
        Returns:
            ExecItem: Exec created successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Invalid request body
                HTTPError: 401: Unauthorized
                HTTPError: 500: Internal Server Error - Failed to create exec
        """
        url = f"{self.base_url}/api/v1/execs"
        
        json_body: CreateExecRequest = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), ExecItem)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), ExecItem)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def list_execs(
        self,
    ) -> ExecListResponse:
        """
        List all execs
        
        Returns a list of all active execs.
        
        Returns:
            ExecListResponse: Execs retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 401: Unauthorized
        """
        url = f"{self.base_url}/api/v1/execs"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), ExecListResponse)
            case 401:
                raise UnauthorisedError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), ExecListResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def get_exec(
        self,
        id_: str,
    ) -> ExecItem:
        """
        Get exec by ID
        
        Retrieves a specific exec by its ID.
        
        Args:
            id (str)                 : Exec identifier
        
        Returns:
            ExecItem: Exec retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Exec ID is required
                HTTPError: 401: Unauthorized
                HTTPError: 404: Exec not found
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/api/v1/execs/{id_}"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), ExecItem)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), ExecItem)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def update_exec(
        self,
        id_: str,
        body: UpdateExecRequest,
    ) -> ExecItem:
        """
        Update exec
        
        Updates exec status (e.g., start a stopped exec).
        
        Args:
            id (str)                 : Exec identifier
            body (UpdateExecRequest) : Exec update request (json)
        
        Returns:
            ExecItem: Exec updated successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Exec ID is required or invalid status
                HTTPError: 401: Unauthorized
                HTTPError: 404: Exec not found
                HTTPError: 409: Conflict - Exec is already in the requested state
                HTTPError: 500: Internal Server Error - Failed to update exec
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/api/v1/execs/{id_}"
        
        json_body: UpdateExecRequest = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("PUT", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), ExecItem)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case 409:
                raise ConflictError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), ExecItem)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def delete_exec(
        self,
        id_: str,
    ) -> ExecDeleteResponse:
        """
        Delete Exec
        
        Deletes a exec and execs its process.
        
        Args:
            id (str)                 : Exec identifier
        
        Returns:
            ExecDeleteResponse: Exec deleted successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Exec ID is required
                HTTPError: 401: Unauthorized
                HTTPError: 404: Exec not found
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/api/v1/execs/{id_}"
        
        response = await self._transport.request(
            "DELETE", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), ExecDeleteResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), ExecDeleteResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def get_exec_output(
        self,
        id_: str,
        last_sequence: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Get Exec output
        
        Retrieves the plain text output from a exec's buffer.
        
        Args:
            id (str)                 : Exec identifier
            lastSequence (int | None): Last sequence number received by the client. Used to
                                       fetch only new output since that sequence or before if it
                                       is negative.
        
        Returns:
            AsyncIterator[dict[str, Any]]: Exec output retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Exec ID is required
                HTTPError: 401: Unauthorized
                HTTPError: 404: Exec not found
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/api/v1/execs/{id_}/io"
        
        params: dict[str, Any] = {
            **({"lastSequence": DataclassSerializer.serialize(last_sequence)} if last_sequence is not None else {}),
        }
        
        response = await self._transport.request(
            "GET", url,
            params=params,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                async for chunk in iter_sse_events_text(response):
                    yield json.loads(chunk)
                return  # Explicit return for async generator
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case _:  # Default response
                async for chunk in iter_sse_events_text(response):
                    yield json.loads(chunk)
                return  # Explicit return for async generator
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def exec_exec_stdin(
        self,
        id_: str,
        body: ExecStdin,
    ) -> ExecItem:
        """
        exec exec stdin
        
        exec exec command (e.g., npm install).
        
        Args:
            id (str)                 : Exec identifier
            body (ExecStdin)         : Exec update request (json)
        
        Returns:
            ExecItem: Exec stdin executed successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Exec ID is required or invalid status
                HTTPError: 401: Unauthorized
                HTTPError: 404: Exec not found
                HTTPError: 500: Internal Server Error - Failed to update exec
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/api/v1/execs/{id_}/io"
        
        json_body: ExecStdin = DataclassSerializer.serialize(body)
        
        response = await self._transport.request("POST", url, params=None, json=json_body, headers=None)
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), ExecItem)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), ExecItem)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def connect_to_exec_web_socket(
        self,
        id_: str,
    ) -> Error:
        """
        Connect to exec via WebSocket
        
        Establishes a WebSocket connection for real-time exec interaction.  Authentication can
        be provided via: - Authorization header: `Authorization: Bearer <token>` - Query
        parameter: `?token=<token>`  Permissions: - Admin users: Can send input and receive
        output - Readonly users: Can only receive output
        
        Args:
            id (str)                 : Exec identifier
        
        Returns:
            Error: Unexpected Error
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Exec ID is required
                HTTPError: 401: Unauthorized - Authentication token required or invalid
                HTTPError: 404: Exec not found
                HTTPError: 500: Internal Server Error - Failed to establish WebSocket connection
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/ws/v1/execs/{id_}"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 101:
                raise Error101(response=response)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), Error)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def stream_execs_list(
        self,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        List all execs
        
        Returns a list of all active execs using SSE.
        
        Returns:
            AsyncIterator[dict[str, Any]]: Execs retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 401: Unauthorized
        """
        url = f"{self.base_url}/api/v1/stream/execs"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                async for chunk in iter_sse_events_text(response):
                    yield json.loads(chunk)
                return  # Explicit return for async generator
            case 401:
                raise UnauthorisedError(response=response)
            case _:  # Default response
                async for chunk in iter_sse_events_text(response):
                    yield json.loads(chunk)
                return  # Explicit return for async generator
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
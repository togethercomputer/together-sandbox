import json
from typing import Any, AsyncIterator, List, Protocol, runtime_checkable

from together_sandbox.core import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    UnauthorisedError,
)
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_sse_events_text
from together_sandbox.core.utils import DataclassSerializer

from ..models.file_action_request import FileActionRequest
from ..models.file_action_response import FileActionResponse
from ..models.file_create_request import FileCreateRequest
from ..models.file_info import FileInfo
from ..models.file_operation_response import FileOperationResponse
from ..models.file_read_response import FileReadResponse


@runtime_checkable
class FilesClientProtocol(Protocol):
    """Protocol defining the interface of FilesClient for dependency injection."""

    async def create_file(
        self,
        path: str,
        body: FileCreateRequest | None = None,
    ) -> FileReadResponse: ...

    async def read_file(
        self,
        path: str,
    ) -> FileReadResponse: ...

    async def perform_file_action(
        self,
        path: str,
        body: FileActionRequest,
    ) -> FileActionResponse: ...

    async def delete_file(
        self,
        path: str,
    ) -> FileOperationResponse: ...

    async def get_file_stat(
        self,
        path: str,
    ) -> FileInfo: ...

    def create_watcher(
        self,
        path: str,
        recursive: bool | None = None,
        ignore_patterns: List[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]: ...


class FilesClient(FilesClientProtocol):
    """Client for files endpoints. Uses HttpTransport for all HTTP and header management."""

    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url

    async def create_file(
        self,
        path: str,
        body: FileCreateRequest | None = None,
    ) -> FileReadResponse:
        """
        Create a file

        Creates a new file at the specified path with optional content.

        Args:
            path (str)               : File path
            body (FileCreateRequest | None)
                                     : File creation request (json)

        Returns:
            FileReadResponse: File created successfully

        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required or invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 500: Internal Server Error - Failed to create file
        """
        path = DataclassSerializer.serialize(path)

        url = f"{self.base_url}/api/v1/files/{path}"

        json_body: FileCreateRequest | None = DataclassSerializer.serialize(body)

        response = await self._transport.request(
            "POST", url, params=None, json=json_body, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), FileReadResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), FileReadResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def read_file(
        self,
        path: str,
    ) -> FileReadResponse:
        """
        Read file content

        Reads the content of a file at the specified path.

        Args:
            path (str)               : File path

        Returns:
            FileReadResponse: File content retrieved successfully

        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required or invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 404: File not found
        """
        path = DataclassSerializer.serialize(path)

        url = f"{self.base_url}/api/v1/files/{path}"

        response = await self._transport.request(
            "GET", url, params=None, json=None, data=None, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), FileReadResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), FileReadResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def perform_file_action(
        self,
        path: str,
        body: FileActionRequest,
    ) -> FileActionResponse:
        """
        Perform file actions

        Performs actions on files (e.g., move operations).

        Args:
            path (str)               : Source file path (will be URL decoded)
            body (FileActionRequest) : File action request (json)

        Returns:
            FileActionResponse: Action performed successfully

        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required, invalid action, or missing
                           destination
                HTTPError: 401: Unauthorized
                HTTPError: 500: Internal Server Error - Failed to perform action
        """
        path = DataclassSerializer.serialize(path)

        url = f"{self.base_url}/api/v1/files/{path}"

        json_body: FileActionRequest = DataclassSerializer.serialize(body)

        response = await self._transport.request(
            "PATCH", url, params=None, json=json_body, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), FileActionResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), FileActionResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def delete_file(
        self,
        path: str,
    ) -> FileOperationResponse:
        """
        Delete a file

        Deletes a file at the specified path.

        Args:
            path (str)               : File path

        Returns:
            FileOperationResponse: File deleted successfully

        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required or invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 404: File not found
                HTTPError: 500: Internal Server Error - Failed to delete file
        """
        path = DataclassSerializer.serialize(path)

        url = f"{self.base_url}/api/v1/files/{path}"

        response = await self._transport.request(
            "DELETE", url, params=None, json=None, data=None, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), FileOperationResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), FileOperationResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def get_file_stat(
        self,
        path: str,
    ) -> FileInfo:
        """
        Get file stat

        Reads the file metadata.

        Args:
            path (str)               : File path

        Returns:
            FileInfo: File metadata retrieved successfully

        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required or invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 404: File not found
        """
        path = DataclassSerializer.serialize(path)

        url = f"{self.base_url}/api/v1/file_stat/{path}"

        response = await self._transport.request(
            "GET", url, params=None, json=None, data=None, headers=None
        )

        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), FileInfo)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), FileInfo)
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

    async def create_watcher(
        self,
        path: str,
        recursive: bool | None = None,
        ignore_patterns: List[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Watch directory changes using Server-Sent Events (SSE)

        Watch a directory for file system changes and stream events via SSE.

        Args:
            path (str)               : Directory path to watch
            recursive (bool | None)  : Whether to watch directories recursively
            ignorePatterns (List[str] | None)
                                     : Glob patterns to ignore certain files or directories (can
                                       be specified multiple times)

        Returns:
            AsyncIterator[dict[str, Any]]: Directory watcher stream started successfully

        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required or invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 500: Internal Server Error - Failed to create file
        """
        path = DataclassSerializer.serialize(path)

        url = f"{self.base_url}/api/v1/stream/directories/watcher/{path}"

        params: dict[str, Any] = {
            **(
                {"recursive": DataclassSerializer.serialize(recursive)}
                if recursive is not None
                else {}
            ),
            **(
                {"ignorePatterns": DataclassSerializer.serialize(ignore_patterns)}
                if ignore_patterns is not None
                else {}
            ),
        }

        response = await self._transport.request(
            "GET", url, params=params, json=None, data=None, headers=None
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
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                async for chunk in iter_sse_events_text(response):
                    yield json.loads(chunk)
                return  # Explicit return for async generator
        # All paths above should return or raise - this should never execute
        raise RuntimeError("Unexpected code path")  # pragma: no cover

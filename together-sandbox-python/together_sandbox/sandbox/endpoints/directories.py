from typing import Callable, NoReturn, Optional, Protocol, cast, runtime_checkable

from ..models.directory_list_response import DirectoryListResponse
from ..models.file_operation_response import FileOperationResponse
from together_sandbox.core import BadRequestError, InternalServerError, NotFoundError, UnauthorisedError
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_bytes
from together_sandbox.core.utils import DataclassSerializer

from ..models.directory_list_response import DirectoryListResponse
from ..models.file_operation_response import FileOperationResponse

@runtime_checkable
class DirectoriesClientProtocol(Protocol):
    """Protocol defining the interface of DirectoriesClient for dependency injection."""
    
    async def create_directory(
    self,
    path: str,
    ) -> FileOperationResponse: ...
    
    async def list_directory(
    self,
    path: str,
    ) -> DirectoryListResponse: ...
    
    async def delete_directory(
    self,
    path: str,
    ) -> FileOperationResponse: ...
    


class DirectoriesClient(DirectoriesClientProtocol):
    """Client for directories endpoints. Uses HttpTransport for all HTTP and header management."""
    
    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url
    
    async def create_directory(
        self,
        path: str,
    ) -> FileOperationResponse:
        """
        Create a directory
        
        Creates a new directory at the specified path.
        
        Args:
            path (str)               : Directory path
        
        Returns:
            FileOperationResponse: Directory created successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required or invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 500: Internal Server Error - Failed to create directory
        """
        path = DataclassSerializer.serialize(path)
        
        url = f"{self.base_url}/api/v1/directories/{path}"
        
        response = await self._transport.request(
            "POST", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 201:
                return structure_from_dict(response.json(), FileOperationResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), FileOperationResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def list_directory(
        self,
        path: str,
    ) -> DirectoryListResponse:
        """
        List directory contents
        
        Lists the contents of a directory at the specified path.
        
        Args:
            path (str)               : Directory path (will be URL decoded). Use "/" for root
                                       directory.
        
        Returns:
            DirectoryListResponse: Directory contents retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 404: Directory not found
        """
        path = DataclassSerializer.serialize(path)
        
        url = f"{self.base_url}/api/v1/directories/{path}"
        
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
                return structure_from_dict(response.json(), DirectoryListResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), DirectoryListResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def delete_directory(
        self,
        path: str,
    ) -> FileOperationResponse:
        """
        Delete a directory
        
        Deletes a directory at the specified path.
        
        Args:
            path (str)               : Directory path
        
        Returns:
            FileOperationResponse: Directory deleted successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Path is required or invalid path
                HTTPError: 401: Unauthorized
                HTTPError: 404: Directory not found
                HTTPError: 500: Internal Server Error - Failed to delete directory
        """
        path = DataclassSerializer.serialize(path)
        
        url = f"{self.base_url}/api/v1/directories/{path}"
        
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
        raise RuntimeError('Unexpected code path')  # pragma: no cover
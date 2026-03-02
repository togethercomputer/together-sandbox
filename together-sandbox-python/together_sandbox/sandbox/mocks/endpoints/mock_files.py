from typing import Any, NoReturn, TYPE_CHECKING

from ...models.file_action_request import FileActionRequest
from ...models.file_action_response import FileActionResponse
from ...models.file_create_request import FileCreateRequest
from ...models.file_info import FileInfo
from ...models.file_operation_response import FileOperationResponse
from ...models.file_read_response import FileReadResponse
from together_sandbox.core import BadRequestError, InternalServerError, NotFoundError, UnauthorisedError
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.utils import DataclassSerializer

from ...models.file_action_request import FileActionRequest
from ...models.file_action_response import FileActionResponse
from ...models.file_create_request import FileCreateRequest
from ...models.file_info import FileInfo
from ...models.file_operation_response import FileOperationResponse
from ...models.file_read_response import FileReadResponse

if TYPE_CHECKING:
    from ...endpoints.files import FilesClientProtocol

class MockFilesClient:
    """
    Mock implementation of FilesClient for testing.
    
    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.
    
    Example:
        class TestFilesClient(MockFilesClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """
    
    async def create_file(
    self,
    path: str,
    body: FileCreateRequest | None = None,
    ) -> FileReadResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockFilesClient.create_file() not implemented. Override this method in your test subclass.")
    
    
    async def read_file(
    self,
    path: str,
    ) -> FileReadResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockFilesClient.read_file() not implemented. Override this method in your test subclass.")
    
    
    async def perform_file_action(
    self,
    path: str,
    body: FileActionRequest,
    ) -> FileActionResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockFilesClient.perform_file_action() not implemented. Override this method in your test subclass.")
    
    
    async def delete_file(
    self,
    path: str,
    ) -> FileOperationResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockFilesClient.delete_file() not implemented. Override this method in your test subclass.")
    
    
    async def get_file_stat(
    self,
    path: str,
    ) -> FileInfo:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockFilesClient.get_file_stat() not implemented. Override this method in your test subclass.")
from typing import Any, Dict, NoReturn, TYPE_CHECKING

from ...models.sandbox_create_request import SandboxCreateRequest
from ...models.sandbox_create_response import SandboxCreateResponse
from ...models.sandbox_fork_request import SandboxForkRequest
from ...models.sandbox_fork_response import SandboxForkResponse
from ...models.sandbox_get_response import SandboxGetResponse
from ...models.sandbox_list_response import SandboxListResponse
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.utils import DataclassSerializer

from ...models.sandbox_create_request import SandboxCreateRequest
from ...models.sandbox_create_response import SandboxCreateResponse
from ...models.sandbox_fork_request import SandboxForkRequest
from ...models.sandbox_fork_response import SandboxForkResponse
from ...models.sandbox_get_response import SandboxGetResponse
from ...models.sandbox_list_response import SandboxListResponse

if TYPE_CHECKING:
    from ...endpoints.sandbox import SandboxClientProtocol

class MockSandboxClient:
    """
    Mock implementation of SandboxClient for testing.
    
    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.
    
    Example:
        class TestSandboxClient(MockSandboxClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """
    
    async def sandbox_list(
    self,
    tags: str | None = None,
    order_by: str | None = None,
    direction: str | None = None,
    page_size: int | None = None,
    page: int | None = None,
    status: str | None = None,
    ) -> SandboxListResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockSandboxClient.sandbox_list() not implemented. Override this method in your test subclass.")
    
    
    async def sandbox_create(
    self,
    body: SandboxCreateRequest | None = None,
    ) -> SandboxCreateResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockSandboxClient.sandbox_create() not implemented. Override this method in your test subclass.")
    
    
    async def sandbox_get(
    self,
    id_: str,
    ) -> SandboxGetResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockSandboxClient.sandbox_get() not implemented. Override this method in your test subclass.")
    
    
    async def sandbox_fork(
    self,
    id_: str,
    body: SandboxForkRequest | None = None,
    ) -> SandboxForkResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockSandboxClient.sandbox_fork() not implemented. Override this method in your test subclass.")
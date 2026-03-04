from typing import NoReturn, TYPE_CHECKING

from ...models.meta_information import MetaInformation
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport

from ...models.meta_information import MetaInformation

if TYPE_CHECKING:
    from ...endpoints.meta import MetaClientProtocol

class MockMetaClient:
    """
    Mock implementation of MetaClient for testing.
    
    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.
    
    Example:
        class TestMetaClient(MockMetaClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """
    
    async def meta_info(
    self,
    ) -> MetaInformation:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockMetaClient.meta_info() not implemented. Override this method in your test subclass.")
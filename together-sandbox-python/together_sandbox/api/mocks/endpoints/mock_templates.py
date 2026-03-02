from typing import Any, NoReturn, TYPE_CHECKING

from ...models.template_create_request_common import TemplateCreateRequestCommon
from ...models.template_create_response import TemplateCreateResponse
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.utils import DataclassSerializer

from ...models.template_create_request_common import TemplateCreateRequestCommon
from ...models.template_create_response import TemplateCreateResponse

if TYPE_CHECKING:
    from ...endpoints.templates import TemplatesClientProtocol

class MockTemplatesClient:
    """
    Mock implementation of TemplatesClient for testing.
    
    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.
    
    Example:
        class TestTemplatesClient(MockTemplatesClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """
    
    async def templates_create(
    self,
    body: TemplateCreateRequestCommon | None = None,
    ) -> TemplateCreateResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockTemplatesClient.templates_create() not implemented. Override this method in your test subclass.")
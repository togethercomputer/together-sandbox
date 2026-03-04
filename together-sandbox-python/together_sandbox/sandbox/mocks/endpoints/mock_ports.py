from typing import Any, AsyncIterator, Dict, NoReturn, TYPE_CHECKING

from ...models.ports_list_response import PortsListResponse
from together_sandbox.core import InternalServerError, UnauthorisedError
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_sse_events_text

import collections.abc
import json

from ...models.ports_list_response import PortsListResponse

if TYPE_CHECKING:
    from ...endpoints.ports import PortsClientProtocol

class MockPortsClient:
    """
    Mock implementation of PortsClient for testing.
    
    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.
    
    Example:
        class TestPortsClient(MockPortsClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """
    
    async def list_ports(
    self,
    ) -> PortsListResponse:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockPortsClient.list_ports() not implemented. Override this method in your test subclass.")
    
    
    async def stream_ports_list(
    self,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockPortsClient.stream_ports_list() not implemented. Override this method in your test subclass.")
        yield  # pragma: no cover
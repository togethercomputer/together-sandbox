from typing import Any, AsyncIterator, Dict, List, NoReturn, TYPE_CHECKING

from together_sandbox.core import BadRequestError, InternalServerError, UnauthorisedError
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_sse_events_text
from together_sandbox.core.utils import DataclassSerializer

import collections.abc
import json

if TYPE_CHECKING:
    from ...endpoints.streams import StreamsClientProtocol

class MockStreamsClient:
    """
    Mock implementation of StreamsClient for testing.
    
    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.
    
    Example:
        class TestStreamsClient(MockStreamsClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """
    
    async def create_watcher(
    self,
    path: str,
    recursive: bool | None = None,
    ignore_patterns: List[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Mock implementation that raises NotImplementedError.
        
        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError("MockStreamsClient.create_watcher() not implemented. Override this method in your test subclass.")
        yield  # pragma: no cover
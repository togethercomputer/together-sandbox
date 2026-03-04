from typing import Any, AsyncIterator, Callable, Dict, NoReturn, Optional, Protocol, cast, runtime_checkable

from ..models.ports_list_response import PortsListResponse
from together_sandbox.core import InternalServerError, UnauthorisedError
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_bytes, iter_sse_events_text

import collections.abc
import json

from ..models.ports_list_response import PortsListResponse

@runtime_checkable
class PortsClientProtocol(Protocol):
    """Protocol defining the interface of PortsClient for dependency injection."""
    
    async def list_ports(
    self,
    ) -> PortsListResponse: ...
    
    def stream_ports_list(
    self,
    ) -> AsyncIterator[dict[str, Any]]: ...
    


class PortsClient(PortsClientProtocol):
    """Client for ports endpoints. Uses HttpTransport for all HTTP and header management."""
    
    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url
    
    async def list_ports(
        self,
    ) -> PortsListResponse:
        """
        List open ports
        
        Lists all open TCP ports on the system, excluding ignored ports configured in the
        server.
        
        Returns:
            PortsListResponse: Open ports retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 401: Unauthorized
                HTTPError: 500: Internal Server Error - Failed to read port information
        """
        url = f"{self.base_url}/api/v1/ports"
        
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
                return structure_from_dict(response.json(), PortsListResponse)
            case 401:
                raise UnauthorisedError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), PortsListResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def stream_ports_list(
        self,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        List open ports using Server-Sent Events (SSE)
        
        Lists all open TCP ports on the system AND LISTEN TO THE CHANGES, excluding ignored
        ports configured in the server.
        
        Returns:
            AsyncIterator[dict[str, Any]]: Open ports retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 401: Unauthorized
                HTTPError: 500: Internal Server Error - Failed to read port information
        """
        url = f"{self.base_url}/api/v1/stream/ports"
        
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
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                async for chunk in iter_sse_events_text(response):
                    yield json.loads(chunk)
                return  # Explicit return for async generator
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
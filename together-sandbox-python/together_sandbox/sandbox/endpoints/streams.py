import json
from typing import Any, AsyncIterator, List, Protocol, runtime_checkable

from together_sandbox.core import (
    BadRequestError,
    InternalServerError,
    UnauthorisedError,
)
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_sse_events_text
from together_sandbox.core.utils import DataclassSerializer


@runtime_checkable
class StreamsClientProtocol(Protocol):
    """Protocol defining the interface of StreamsClient for dependency injection."""

    def create_watcher(
        self,
        path: str,
        recursive: bool | None = None,
        ignore_patterns: List[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]: ...


class StreamsClient(StreamsClientProtocol):
    """Client for streams endpoints. Uses HttpTransport for all HTTP and header management."""

    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url

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

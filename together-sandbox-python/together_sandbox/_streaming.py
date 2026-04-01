import json
from typing import Any, AsyncGenerator, AsyncIterator, List

import httpx


class SSEEvent:
    def __init__(self, data: str, event: str | None = None, id: str | None = None, retry: int | None = None) -> None:
        self.data: str = data
        self.event: str | None = event
        self.id: str | None = id
        self.retry: int | None = retry

    def __repr__(self) -> str:
        return f"SSEEvent(data={self.data!r}, event={self.event!r}, id={self.id!r}, retry={self.retry!r})"


async def iter_bytes(response: httpx.Response) -> AsyncIterator[bytes]:
    async for chunk in response.aiter_bytes():
        yield chunk


async def iter_ndjson(response: httpx.Response) -> AsyncIterator[Any]:
    async for line in response.aiter_lines():
        line = line.strip()
        if line:
            yield json.loads(line)


async def iter_sse(response: httpx.Response) -> AsyncIterator[SSEEvent]:
    """Parse Server-Sent Events (SSE) from a streaming response."""
    event_lines: list[str] = []
    async for line in response.aiter_lines():
        if line == "":
            # End of event
            if event_lines:
                event = _parse_sse_event(event_lines)
                if event:
                    yield event
                event_lines = []
        else:
            event_lines.append(line)
    # Last event (if any)
    if event_lines:
        event = _parse_sse_event(event_lines)
        if event:
            yield event


def _parse_sse_event(lines: List[str]) -> SSEEvent:
    data = []
    event = None
    id = None
    retry = None
    for line in lines:
        if line.startswith(":"):
            continue  # comment
        if ":" in line:
            field, value = line.split(":", 1)
            value = value.lstrip()
            if field == "data":
                data.append(value)
            elif field == "event":
                event = value
            elif field == "id":
                id = value
            elif field == "retry":
                try:
                    retry = int(value)
                except ValueError:
                    pass
    return SSEEvent(data="\n".join(data), event=event, id=id, retry=retry)


async def iter_sse_events_text(response: httpx.Response) -> AsyncIterator[str]:
    """
    Parses a Server-Sent Events (SSE) stream and yields the `data` field content
    as a string for each event.
    This is specifically for cases where the event data is expected to be a
    single text payload (e.g., a JSON string) per event.
    """
    async for sse_event in iter_sse(response):
        if sse_event.data:  # Ensure data is not empty
            yield sse_event.data


async def stream_sse_json(
    client: httpx.AsyncClient,
    url: str,
    **kwargs: Any,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Open a streaming GET via httpx.AsyncClient.stream() and yield each SSE
    event's ``data`` field as a parsed JSON dict.

    Uses ``.stream()`` (not ``.request()``) to avoid buffering the entire response,
    which would hang indefinitely on long-lived SSE connections.

    Args:
        client: An httpx.AsyncClient (obtained via AuthenticatedClient.get_async_httpx_client()).
        url: The endpoint URL path (relative to the client's base_url).
        **kwargs: Additional kwargs forwarded to httpx.AsyncClient.stream() — e.g.,
                  params={"lastSequence": 5}, headers={...}.

    Yields:
        Parsed JSON dicts from each SSE ``data:`` field (empty data fields are skipped).
    """
    async with client.stream("GET", url, **kwargs) as response:
        async for text in iter_sse_events_text(response):
            yield json.loads(text)

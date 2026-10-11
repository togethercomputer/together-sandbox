"""Tests for SSE streaming facade methods and the stream_sse_json helper."""

from __future__ import annotations

import json
from urllib.parse import quote

import httpx
import pytest

from together_sandbox._sandbox import Execs, Files, Ports
from together_sandbox.sandbox.client import AuthenticatedClient as SandboxAuthClient

# ─── Helpers ──────────────────────────────────────────────────────────────────


class FakeTransport(httpx.AsyncBaseTransport):
    """Fake transport that returns a pre-defined SSE response body."""

    def __init__(self, body: bytes, status_code: int = 200) -> None:
        self._body = body
        self._status_code = status_code

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            self._status_code,
            headers={"Content-Type": "text/event-stream"},
            content=self._body,
        )


class RecordingTransport(httpx.AsyncBaseTransport):
    """Record the request path while returning an empty SSE stream."""

    def __init__(self) -> None:
        self.raw_path: bytes | None = None

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.raw_path = request.url.raw_path
        return httpx.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            content=b"",
        )


def _sse_body(*events: dict) -> bytes:
    """Build a valid SSE response body from dicts."""
    lines: list[str] = []
    for event in events:
        lines.append(f"data: {json.dumps(event)}")
        lines.append("")  # blank line = event separator
    return "\n".join(lines).encode()


def _make_sandbox_client(body: bytes) -> SandboxAuthClient:
    """Create a SandboxAuthClient with a FakeTransport returning the given body."""
    fake_transport = FakeTransport(body)
    client = SandboxAuthClient(
        base_url="http://fake-sandbox",
        token="test-token",
    )
    # Inject the fake async client
    client.set_async_httpx_client(
        httpx.AsyncClient(transport=fake_transport, base_url="http://fake-sandbox")
    )
    return client


@pytest.mark.asyncio
async def test_execs_stream_output():
    """stream_output() parses SSE frames and yields dicts."""
    payload = [{"type": "stdout", "data": "hello"}, {"type": "stdout", "data": "world"}]
    client = _make_sandbox_client(_sse_body(*payload))
    facade = Execs(client)
    results = []
    async for event in facade.stream_output("exec-123"):
        results.append(event)
    assert results == payload


@pytest.mark.asyncio
async def test_stream_handles_empty_data_fields():
    """SSE events with empty data: lines are skipped."""
    body = b'data: \n\ndata: {"key": "val"}\n\n'
    client = _make_sandbox_client(body)
    facade = Execs(client)
    results = []
    async for event in facade.stream_list():
        results.append(event)
    # Empty data events should be skipped; only non-empty ones yielded
    assert len(results) == 1
    assert results[0] == {"key": "val"}


@pytest.mark.asyncio
async def test_stream_handles_sse_comments():
    """Comment lines (: comment) are ignored."""
    body = b': this is a comment\ndata: {"k": 1}\n\n'
    client = _make_sandbox_client(body)
    facade = Execs(client)
    results = []
    async for event in facade.stream_list():
        results.append(event)
    assert results == [{"k": 1}]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/workspace/report#draft", "/workspace/report?draft"])
async def test_watch_encodes_reserved_path_characters(path: str):
    """watch() must keep URL-reserved characters inside the directory path."""
    transport = RecordingTransport()
    client = SandboxAuthClient(base_url="http://fake-sandbox", token="test-token")
    client.set_async_httpx_client(
        httpx.AsyncClient(transport=transport, base_url="http://fake-sandbox")
    )

    async for _ in Files(client).watch(path):
        pass

    assert transport.raw_path == (
        b"/api/v1/stream/directories/watcher/"
        + quote(path, safe="").encode()
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("exec_id", ["exec#draft", "exec?draft"])
async def test_stream_output_encodes_reserved_id_characters(exec_id: str):
    """stream_output() must keep URL-reserved characters inside the exec ID."""
    transport = RecordingTransport()
    client = SandboxAuthClient(base_url="http://fake-sandbox", token="test-token")
    client.set_async_httpx_client(
        httpx.AsyncClient(transport=transport, base_url="http://fake-sandbox")
    )

    async for _ in Execs(client).stream_output(exec_id):
        pass

    assert transport.raw_path == (
        b"/api/v1/stream/execs/" + quote(exec_id, safe="").encode() + b"/io"
    )

"""Tests for SSE streaming facade methods and the stream_sse_json helper."""

from __future__ import annotations

import json

import httpx
import pytest

from together_sandbox._sandbox import Execs
from together_sandbox._streaming import stream_sse_json
from together_sandbox._sandbox_client.client import AuthenticatedClient as SandboxAuthClient

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
async def test_stream_sse_json_parses_frames():
    """stream_sse_json parses SSE frames and yields the raw decoded dicts."""
    payload = [{"type": "stdout", "data": "hello"}, {"type": "stdout", "data": "world"}]
    client = _make_sandbox_client(_sse_body(*payload))
    results = []
    async for event in stream_sse_json(client.get_async_httpx_client(), "/x"):
        results.append(event)
    assert results == payload


@pytest.mark.asyncio
async def test_stream_handles_empty_data_fields():
    """SSE events with empty data: lines are skipped."""
    body = b'data: \n\ndata: {"key": "val"}\n\n'
    client = _make_sandbox_client(body)
    results = []
    async for event in stream_sse_json(client.get_async_httpx_client(), "/x"):
        results.append(event)
    # Empty data events should be skipped; only non-empty ones yielded
    assert len(results) == 1
    assert results[0] == {"key": "val"}


@pytest.mark.asyncio
async def test_stream_handles_sse_comments():
    """Comment lines (: comment) are ignored."""
    body = b': this is a comment\ndata: {"k": 1}\n\n'
    client = _make_sandbox_client(body)
    results = []
    async for event in stream_sse_json(client.get_async_httpx_client(), "/x"):
        results.append(event)
    assert results == [{"k": 1}]


@pytest.mark.asyncio
async def test_execs_stream_output_yields_typed_events():
    """Execs.stream_output() converts raw SSE dicts into ExecOutputEvent facades."""
    payload = [
        {"type": "stdout", "output": "hello", "sequence": 0},
        {"type": "stderr", "output": "oops", "sequence": 1, "exitCode": 3},
    ]
    client = _make_sandbox_client(_sse_body(*payload))
    facade = Execs(client)
    events = []
    async for event in facade.stream_output("exec-123"):
        events.append(event)

    assert [e.type for e in events] == ["stdout", "stderr"]
    assert [e.output for e in events] == ["hello", "oops"]
    assert events[0].exit_code is None
    assert events[1].exit_code == 3

"""Unit tests for Files.read_raw content negotiation."""

from __future__ import annotations

import base64

import httpx
import pytest

from together_sandbox._sandbox import Files
from together_sandbox._utils import RetryConfig
from together_sandbox.errors import HttpError
from together_sandbox.sandbox.client import AuthenticatedClient

BINARY = b"\x89PNG\r\n\x1a\n\x00\xff\xfe"


def make_files(handler) -> tuple[Files, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = AuthenticatedClient(
        base_url="http://agent.test",
        token="token",
        httpx_args={"transport": httpx.MockTransport(record)},
    )
    return Files(client, retry=RetryConfig(max_attempts=1)), requests


async def test_read_raw_requests_octet_stream_from_read_endpoint():
    files, requests = make_files(
        lambda _: httpx.Response(
            200,
            content=BINARY,
            headers={"Content-Type": "application/octet-stream"},
        )
    )

    result = await files.read_raw("/assets/logo.png")

    assert result == BINARY
    assert requests[0].method == "GET"
    assert requests[0].url.raw_path == b"/api/v1/files/%2Fassets%2Flogo.png"
    assert requests[0].headers["Accept"] == "application/octet-stream"


async def test_read_raw_returns_empty_bytes_for_empty_file():
    files, _ = make_files(
        lambda _: httpx.Response(
            200, content=b"", headers={"Content-Type": "application/octet-stream"}
        )
    )

    assert await files.read_raw("/empty.bin") == b""


@pytest.mark.parametrize(
    ("content", "encoding", "expected"),
    [
        (base64.b64encode(BINARY).decode(), "base64", BINARY),
        ("Hello 世界", "utf-8", "Hello 世界".encode()),
    ],
)
async def test_read_raw_decodes_json_from_agents_without_negotiation(
    content, encoding, expected
):
    files, _ = make_files(
        lambda _: httpx.Response(
            200,
            json={"path": "/file", "content": content, "encoding": encoding},
        )
    )

    assert await files.read_raw("/file") == expected


async def test_read_raw_raises_http_error_on_not_found():
    files, _ = make_files(
        lambda _: httpx.Response(404, json={"code": 404, "message": "File not found"})
    )

    with pytest.raises(HttpError) as exc_info:
        await files.read_raw("/missing.bin")

    assert exc_info.value.status == 404
    assert "File not found" in str(exc_info.value)


async def test_read_sends_no_octet_stream_accept_header():
    files, requests = make_files(
        lambda _: httpx.Response(
            200, json={"path": "/file", "content": "text", "encoding": "utf-8"}
        )
    )

    assert await files.read("/file") == "text"
    assert "application/octet-stream" not in requests[0].headers.get("Accept", "")

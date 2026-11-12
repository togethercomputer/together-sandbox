"""Unit tests for Files.read_raw content negotiation."""

from __future__ import annotations

import base64
import json
from typing import Any

import pytest

from together_sandbox._sandbox import Files
from together_sandbox._utils import RetryConfig
from together_sandbox.errors import HttpError
from together_sandbox.sandbox.client import AuthenticatedClient

BINARY = b"\x89PNG\r\n\x1a\n\x00\xff\xfe"

# ─── Helpers ─────────────────────────────────────────────────────────────────
#
# The generated client is built on httpx or httpx2 depending on the
# openapi-python-client version used to generate it, so these tests stub the
# async client instead of using either library's MockTransport.


class FakeResponse:
    def __init__(self, status_code: int, content: bytes, content_type: str) -> None:
        self.status_code = status_code
        self.content = content
        self.headers = {"content-type": content_type}

    def json(self) -> Any:
        return json.loads(self.content)


class FakeAsyncClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.requests: list[dict[str, Any]] = []

    async def request(self, **kwargs: Any) -> FakeResponse:
        self.requests.append(kwargs)
        return self.response


def octet_stream_response(content: bytes) -> FakeResponse:
    return FakeResponse(200, content, "application/octet-stream")


def json_response(status_code: int, body: Any) -> FakeResponse:
    return FakeResponse(status_code, json.dumps(body).encode(), "application/json")


def make_files(response: FakeResponse) -> tuple[Files, FakeAsyncClient]:
    fake = FakeAsyncClient(response)
    client = AuthenticatedClient(base_url="http://agent.test", token="token")
    client.set_async_httpx_client(fake)  # type: ignore[arg-type]
    return Files(client, retry=RetryConfig(max_attempts=1)), fake


# ─── read_raw ────────────────────────────────────────────────────────────────


async def test_read_raw_requests_octet_stream_from_read_endpoint():
    files, fake = make_files(octet_stream_response(BINARY))

    result = await files.read_raw("/assets/logo.png")

    assert result == BINARY
    assert fake.requests[0]["method"] == "get"
    assert fake.requests[0]["url"] == "/api/v1/files/%2Fassets%2Flogo.png"
    assert fake.requests[0]["headers"]["Accept"] == "application/octet-stream"


async def test_read_raw_returns_empty_bytes_for_empty_file():
    files, _ = make_files(octet_stream_response(b""))

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
        json_response(200, {"path": "/file", "content": content, "encoding": encoding})
    )

    assert await files.read_raw("/file") == expected


async def test_read_raw_raises_http_error_on_not_found():
    files, _ = make_files(
        json_response(404, {"code": 404, "message": "File not found"})
    )

    with pytest.raises(HttpError) as exc_info:
        await files.read_raw("/missing.bin")

    assert exc_info.value.status == 404
    assert "File not found" in str(exc_info.value)


# ─── read ────────────────────────────────────────────────────────────────────


async def test_read_sends_no_octet_stream_accept_header():
    files, fake = make_files(
        json_response(200, {"path": "/file", "content": "text", "encoding": "utf-8"})
    )

    assert await files.read("/file") == "text"
    headers = fake.requests[0].get("headers", {})
    assert "application/octet-stream" not in headers.get("Accept", "")

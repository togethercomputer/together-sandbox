"""Unit tests for the Together Sandbox unified facade."""

from __future__ import annotations

import io
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from together_sandbox.facade import (
    _resolve_connection,
    Directories,
    Execs,
    Files,
    Ports,
    Sandbox,
    Tasks,
    TogetherSandbox,
)
from together_sandbox.sandbox.models.file_read_response import FileReadResponse
from together_sandbox.sandbox.types import File
from together_sandbox.api.models.sandbox import Sandbox as SandboxModel


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_sandbox_model(**overrides) -> MagicMock:
    """Build a mock SandboxModel with sensible defaults."""
    defaults = dict(
        id="test-sandbox-123",
        agent_url="https://agent.example.com",
        agent_token="agent-tok",
    )
    defaults.update(overrides)
    mock = MagicMock(spec=SandboxModel)
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


# ─── _resolve_connection tests ────────────────────────────────────────────────


class TestResolveConnection:
    def test_returns_agent_url_and_token(self):
        sandbox = _make_sandbox_model()
        url, token = _resolve_connection(sandbox)
        assert url == "https://agent.example.com"
        assert token == "agent-tok"

    def test_raises_if_agent_url_missing(self):
        sandbox = _make_sandbox_model(agent_url=None)
        with pytest.raises(RuntimeError, match="no agent connection details"):
            _resolve_connection(sandbox)

    def test_raises_if_agent_token_missing(self):
        sandbox = _make_sandbox_model(agent_token=None)
        with pytest.raises(RuntimeError, match="no agent connection details"):
            _resolve_connection(sandbox)


# ─── TogetherSandbox tests ───────────────────────────────────────────────────


class TestTogetherSandbox:
    def test_raises_without_api_key(self, monkeypatch):
        monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key must be provided"):
            TogetherSandbox()

    def test_reads_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("TOGETHER_API_KEY", "test-key-from-env")
        sdk = TogetherSandbox()
        assert sdk.sandboxes is not None

    def test_accepts_explicit_api_key(self, monkeypatch):
        monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
        sdk = TogetherSandbox(api_key="explicit-key")
        assert sdk.sandboxes is not None


# ─── Sandbox tests ────────────────────────────────────────────────────


class TestSandbox:
    def test_id_property(self):
        vm_info = _make_sandbox_model(id="test-id-456")
        mock_sandbox_client = MagicMock()
        mock_api_client = MagicMock()
        sb = Sandbox(vm_info, mock_sandbox_client, mock_api_client)
        assert sb.id == "test-id-456"

    def test_id_raises_when_none(self):
        sb = Sandbox(_make_sandbox_model(id=None), MagicMock(), MagicMock())
        with pytest.raises(RuntimeError, match="no ID"):
            _ = sb.id

    def test_vm_info_property(self):
        vm_info = _make_sandbox_model()
        sb = Sandbox(vm_info, MagicMock(), MagicMock())
        assert sb.vm_info is vm_info

    def test_delegates_files_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_sandbox_model(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.files, Files)

    def test_delegates_directories_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_sandbox_model(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.directories, Directories)

    def test_delegates_execs_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_sandbox_model(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.execs, Execs)

    def test_delegates_tasks_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_sandbox_model(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.tasks, Tasks)

    def test_delegates_ports_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_sandbox_model(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.ports, Ports)


# ─── FilesFacade tests ────────────────────────────────────────────────────


class TestFiles:
    """Tests for Files.create() binary file creation."""

    @pytest.mark.asyncio
    async def test_create_file_with_string_content(self):
        """Test that create() accepts string content and converts to binary."""
        mock_client = MagicMock()
        facade = Files(mock_client)

        # Mock the API response
        mock_response = FileReadResponse(
            path="/test.txt",
            content="Hello, world!",
        )

        with patch(
            "together_sandbox.facade.create_file_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await facade.create("/test.txt", "Hello, world!")

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify the client was passed
            assert call_args.kwargs["client"] == mock_client

            # Verify the path was passed
            assert call_args.args[0] == "/test.txt"

            # Verify a File object was created with binary content
            file_arg = call_args.kwargs["body"]
            assert isinstance(file_arg, File)
            assert isinstance(file_arg.payload, io.BytesIO)

            # Verify the content was encoded to UTF-8
            file_arg.payload.seek(0)
            content = file_arg.payload.read()
            assert content == b"Hello, world!"

            # Verify the response (unwrapped to content string)
            assert result == "Hello, world!"

    @pytest.mark.asyncio
    async def test_create_file_with_bytes_content(self):
        """Test that create() accepts bytes content directly."""
        mock_client = MagicMock()
        facade = Files(mock_client)

        # Binary content (e.g., image data)
        binary_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

        mock_response = FileReadResponse(
            path="/image.png",
            content="[binary]",
        )

        with patch(
            "together_sandbox.facade.create_file_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await facade.create("/image.png", binary_data)

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify a File object was created with the binary content
            file_arg = call_args.kwargs["body"]
            assert isinstance(file_arg, File)
            assert isinstance(file_arg.payload, io.BytesIO)

            # Verify the content is unchanged
            file_arg.payload.seek(0)
            content = file_arg.payload.read()
            assert content == binary_data

            # Verify the response (unwrapped to content string)
            assert result == "[binary]"

    @pytest.mark.asyncio
    async def test_create_file_with_unicode_content(self):
        """Test that create() properly encodes Unicode characters."""
        mock_client = MagicMock()
        facade = Files(mock_client)

        # Unicode content with emoji and international characters
        unicode_text = "Hello 世界 🌍 Привет"

        mock_response = FileReadResponse(
            path="/unicode.txt",
            content=unicode_text,
        )

        with patch(
            "together_sandbox.facade.create_file_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await facade.create("/unicode.txt", unicode_text)

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify the content was properly encoded to UTF-8
            file_arg = call_args.kwargs["body"]
            file_arg.payload.seek(0)
            content = file_arg.payload.read()

            # Verify it can be decoded back to the original string
            assert content.decode("utf-8") == unicode_text

            # Verify the response (unwrapped to content string)
            assert result == unicode_text

    @pytest.mark.asyncio
    async def test_create_file_empty_content(self):
        """Test that create() handles empty content."""
        mock_client = MagicMock()
        facade = Files(mock_client)

        mock_response = FileReadResponse(
            path="/empty.txt",
            content="",
        )

        with patch(
            "together_sandbox.facade.create_file_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await facade.create("/empty.txt", "")

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify empty content creates an empty BytesIO
            file_arg = call_args.kwargs["body"]
            file_arg.payload.seek(0)
            content = file_arg.payload.read()
            assert content == b""

            # Verify the response (unwrapped to content string)
            assert result == ""

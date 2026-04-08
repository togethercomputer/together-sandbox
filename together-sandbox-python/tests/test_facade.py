"""Unit tests for the Together Sandbox unified facade."""

from __future__ import annotations

import io
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from together_sandbox.facade import (
    _resolve_connection,
    DirectoriesFacade,
    ExecsFacade,
    FilesFacade,
    PortsFacade,
    Sandbox,
    TasksFacade,
    TogetherSandbox,
)
from together_sandbox.api.models.vm_start_response_data import VMStartResponseData
from together_sandbox.api.types import UNSET
from together_sandbox.sandbox.models.file_read_response import FileReadResponse
from together_sandbox.sandbox.types import File


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_vm_info(**overrides) -> VMStartResponseData:
    """Build a VMStartResponseData with sensible defaults."""
    defaults = dict(
        bootup_type="cold",
        cluster="us-east-1",
        id="test-sandbox-123",
        latest_pitcher_version="1.0.0",
        pitcher_manager_version="1.0.0",
        pitcher_token="pitcher-tok",
        pitcher_url="https://pitcher.example.com",
        pitcher_version="1.0.0",
        reconnect_token="reconnect-tok",
        use_pint=False,
        user_workspace_path="/home/user/workspace",
        vm_agent_type="pint",
        workspace_path="/workspace",
        pint_token=UNSET,
        pint_url=UNSET,
    )
    defaults.update(overrides)
    return VMStartResponseData(**defaults)


# ─── _resolve_connection tests ────────────────────────────────────────────────


class TestResolveConnection:
    def test_prefers_pint_when_use_pint_true_and_fields_present(self):
        vm_info = _make_vm_info(
            use_pint=True,
            pint_url="https://pint.example.com",
            pint_token="pint-tok",
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pint.example.com"
        assert token == "pint-tok"

    def test_falls_back_to_pitcher_when_use_pint_false(self):
        vm_info = _make_vm_info(
            use_pint=False,
            pint_url="https://pint.example.com",
            pint_token="pint-tok",
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pitcher.example.com"
        assert token == "pitcher-tok"

    def test_falls_back_to_pitcher_when_pint_url_unset(self):
        vm_info = _make_vm_info(
            use_pint=True,
            pint_url=UNSET,
            pint_token=UNSET,
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pitcher.example.com"
        assert token == "pitcher-tok"

    def test_falls_back_to_pitcher_when_pint_token_unset(self):
        vm_info = _make_vm_info(
            use_pint=True,
            pint_url="https://pint.example.com",
            pint_token=UNSET,
        )
        url, token = _resolve_connection(vm_info)
        assert url == "https://pitcher.example.com"
        assert token == "pitcher-tok"


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
        vm_info = _make_vm_info(id="test-id-456")
        mock_sandbox_client = MagicMock()
        mock_api_client = MagicMock()
        sb = Sandbox(vm_info, mock_sandbox_client, mock_api_client)
        assert sb.id == "test-id-456"

    def test_vm_info_property(self):
        vm_info = _make_vm_info()
        sb = Sandbox(vm_info, MagicMock(), MagicMock())
        assert sb.vm_info is vm_info

    def test_delegates_files_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.files, FilesFacade)

    def test_delegates_directories_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.directories, DirectoriesFacade)

    def test_delegates_execs_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.execs, ExecsFacade)

    def test_delegates_tasks_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.tasks, TasksFacade)

    def test_delegates_ports_namespace(self):
        mock_sandbox_client = MagicMock()
        sb = Sandbox(_make_vm_info(), mock_sandbox_client, MagicMock())
        assert isinstance(sb.ports, PortsFacade)


# ─── FilesFacade tests ────────────────────────────────────────────────────


class TestFilesFacade:
    """Tests for FilesFacade.create_file() binary file creation."""

    @pytest.mark.asyncio
    async def test_create_file_with_string_content(self):
        """Test that create_file accepts string content and converts to binary."""
        mock_client = MagicMock()
        facade = FilesFacade(mock_client)

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
            result = await facade.create_file("/test.txt", "Hello, world!")

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

            # Verify the response
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_create_file_with_bytes_content(self):
        """Test that create_file accepts bytes content directly."""
        mock_client = MagicMock()
        facade = FilesFacade(mock_client)

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
            result = await facade.create_file("/image.png", binary_data)

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

            # Verify the response
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_create_file_with_unicode_content(self):
        """Test that create_file properly encodes Unicode characters."""
        mock_client = MagicMock()
        facade = FilesFacade(mock_client)

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
            result = await facade.create_file("/unicode.txt", unicode_text)

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify the content was properly encoded to UTF-8
            file_arg = call_args.kwargs["body"]
            file_arg.payload.seek(0)
            content = file_arg.payload.read()

            # Verify it can be decoded back to the original string
            assert content.decode("utf-8") == unicode_text

            # Verify the response
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_create_file_empty_content(self):
        """Test that create_file handles empty content."""
        mock_client = MagicMock()
        facade = FilesFacade(mock_client)

        mock_response = FileReadResponse(
            path="/empty.txt",
            content="",
        )

        with patch(
            "together_sandbox.facade.create_file_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await facade.create_file("/empty.txt", "")

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify empty content creates an empty BytesIO
            file_arg = call_args.kwargs["body"]
            file_arg.payload.seek(0)
            content = file_arg.payload.read()
            assert content == b""

            # Verify the response
            assert result == mock_response

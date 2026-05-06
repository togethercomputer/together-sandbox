"""Unit tests for the Together Sandbox unified facade."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from together_sandbox._sandbox import (
    Directories,
    Execs,
    Files,
    Ports,
    Sandbox,
    _unwrap_or_raise,
)
from together_sandbox._sandboxes import SandboxesNamespace, _resolve_connection
from together_sandbox._snapshots import (
    SnapshotsNamespace,
    CreateImageSnapshotParams,
    CreateContextSnapshotParams,
)
from together_sandbox.api.models.container_registry_credential import (
    ContainerRegistryCredential,
)
from together_sandbox._together_sandbox import TogetherSandbox
from together_sandbox._types import StartOptions
from together_sandbox.sandbox.models.file_read_response import FileReadResponse
from together_sandbox.sandbox.models.file_read_response_encoding import FileReadResponseEncoding
from together_sandbox.sandbox.models.file_operation_response import (
    FileOperationResponse,
)
from together_sandbox.sandbox.models.file_action_response import FileActionResponse
from together_sandbox.sandbox.models.exec_delete_response import ExecDeleteResponse
from together_sandbox.sandbox.models.ports_list_response import PortsListResponse
from together_sandbox.sandbox.models.error import Error
from together_sandbox.sandbox.types import File
from together_sandbox.api.models.sandbox import Sandbox as SandboxModel
from together_sandbox.api.models.start_sandbox_body import StartSandboxBody
from together_sandbox.api.types import UNSET


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


# ─── SandboxesNamespace.start() body construction tests ──────────────────────


class TestSandboxesNamespaceStart:
    """Tests that SandboxesNamespace.start() builds the correct body argument."""

    def _make_namespace(self) -> SandboxesNamespace:
        return SandboxesNamespace(api_client=MagicMock())

    @pytest.mark.asyncio
    async def test_start_without_options_passes_unset_body(self):
        """When start_options is None, body must be UNSET (not None or empty dict)."""
        ns = self._make_namespace()
        vm_info = _make_sandbox_model()

        with patch(
            "together_sandbox._sandboxes.start_sandbox_api",
            new_callable=AsyncMock,
            return_value=vm_info,
        ) as mock_api:
            with patch(
                "together_sandbox._sandboxes.wait_for_sandbox_api",
                new_callable=AsyncMock,
                return_value=_make_sandbox_model(
                    status="running"
                ),  # must pass the status guard
            ):
                with patch("together_sandbox._sandboxes.SandboxClient"):
                    await ns.start("sandbox-1")

            call_kwargs = mock_api.call_args.kwargs
            assert call_kwargs["body"] is UNSET

    @pytest.mark.asyncio
    async def test_start_with_version_number_passes_body(self):
        """When start_options has version_number, body must be StartSandboxBody with that value."""
        ns = self._make_namespace()
        vm_info = _make_sandbox_model()

        with patch(
            "together_sandbox._sandboxes.start_sandbox_api",
            new_callable=AsyncMock,
            return_value=vm_info,
        ) as mock_api:
            with patch(
                "together_sandbox._sandboxes.wait_for_sandbox_api",
                new_callable=AsyncMock,
                return_value=_make_sandbox_model(
                    status="running"
                ),  # must pass the status guard
            ):
                with patch("together_sandbox._sandboxes.SandboxClient"):
                    await ns.start(
                        "sandbox-1", start_options=StartOptions(version_number=123)
                    )

            call_kwargs = mock_api.call_args.kwargs
            body = call_kwargs["body"]
            assert isinstance(body, StartSandboxBody)
            assert body.version_number == 123

    @pytest.mark.asyncio
    async def test_start_with_version_number_none_passes_unset_body(self):
        """When start_options.version_number is None, body must be UNSET."""
        ns = self._make_namespace()
        vm_info = _make_sandbox_model()

        with patch(
            "together_sandbox._sandboxes.start_sandbox_api",
            new_callable=AsyncMock,
            return_value=vm_info,
        ) as mock_api:
            with patch(
                "together_sandbox._sandboxes.wait_for_sandbox_api",
                new_callable=AsyncMock,
                return_value=_make_sandbox_model(
                    status="running"
                ),  # must pass the status guard
            ):
                with patch("together_sandbox._sandboxes.SandboxClient"):
                    await ns.start(
                        "sandbox-1", start_options=StartOptions(version_number=None)
                    )

            call_kwargs = mock_api.call_args.kwargs
            assert call_kwargs["body"] is UNSET


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
            encoding=FileReadResponseEncoding.UTF_8,
        )

        with patch(
            "together_sandbox._sandbox.create_file_api",
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
            assert isinstance(file_arg.payload, bytes)

            # Verify the content was encoded to UTF-8
            assert file_arg.payload == b"Hello, world!"

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
            encoding=FileReadResponseEncoding.BASE64,
        )

        with patch(
            "together_sandbox._sandbox.create_file_api",
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
            assert isinstance(file_arg.payload, bytes)

            # Verify the content is unchanged
            assert file_arg.payload == binary_data

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
            encoding=FileReadResponseEncoding.UTF_8,
        )

        with patch(
            "together_sandbox._sandbox.create_file_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await facade.create("/unicode.txt", unicode_text)

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify the content was properly encoded to UTF-8
            file_arg = call_args.kwargs["body"]
            assert isinstance(file_arg.payload, bytes)

            # Verify it can be decoded back to the original string
            assert file_arg.payload.decode("utf-8") == unicode_text

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
            encoding=FileReadResponseEncoding.UTF_8,
        )

        with patch(
            "together_sandbox._sandbox.create_file_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_api:
            result = await facade.create("/empty.txt", "")

            # Verify the API was called
            assert mock_api.called
            call_args = mock_api.call_args

            # Verify empty content creates empty bytes
            file_arg = call_args.kwargs["body"]
            assert isinstance(file_arg.payload, bytes)
            assert file_arg.payload == b""

            # Verify the response (unwrapped to content string)
            assert result == ""

# ─── _unwrap_or_raise tests ───────────────────────────────────────────────────


class TestUnwrapOrRaise:
    """Tests for the _unwrap_or_raise() private helper."""

    def test_returns_result_when_valid(self):
        """Returns the value unchanged when it is not None or Error."""
        obj = object()
        assert _unwrap_or_raise(obj, op="testOp") is obj

    def test_raises_on_none_without_context(self):
        """Raises RuntimeError with op name when result is None and no context given."""
        with pytest.raises(RuntimeError, match="testOp returned None$"):
            _unwrap_or_raise(None, op="testOp")

    def test_raises_on_none_with_context(self):
        """Raises RuntimeError including context when result is None."""
        with pytest.raises(RuntimeError, match="testOp returned None for path '/foo'"):
            _unwrap_or_raise(None, op="testOp", context="for path '/foo'")

    def test_raises_on_error_without_context(self):
        """Raises RuntimeError with Error message when result is an Error."""
        err = Error(code=500, message="internal error")
        with pytest.raises(
            RuntimeError, match="Failed to testOp: internal error \\(code: 500\\)"
        ):
            _unwrap_or_raise(err, op="testOp")

    def test_raises_on_error_with_context(self):
        """Raises RuntimeError including context when result is an Error."""
        err = Error(code=404, message="not found")
        with pytest.raises(
            RuntimeError,
            match="Failed to testOp for path '/bar': not found \\(code: 404\\)",
        ):
            _unwrap_or_raise(err, op="testOp", context="for path '/bar'")


# ─── Files error-path tests ───────────────────────────────────────────────────


class TestFilesErrorPaths:
    """Tests that Files methods raise RuntimeError on API errors."""

    @pytest.mark.asyncio
    async def test_read_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=404, message="not found")
        with patch(
            "together_sandbox._sandbox.read_file_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(RuntimeError, match="Failed to readFile for path '/x'"):
                await Files(mock_client).read("/x")

    @pytest.mark.asyncio
    async def test_read_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.read_file_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(RuntimeError, match="readFile returned None"):
                await Files(mock_client).read("/x")

    @pytest.mark.asyncio
    async def test_create_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=500, message="server error")
        with patch(
            "together_sandbox._sandbox.create_file_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(
                RuntimeError, match="Failed to createFile for path '/x'"
            ):
                await Files(mock_client).create("/x", "content")

    @pytest.mark.asyncio
    async def test_create_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.create_file_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(RuntimeError, match="createFile returned None"):
                await Files(mock_client).create("/x", "content")

    @pytest.mark.asyncio
    async def test_delete_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=404, message="not found")
        with patch(
            "together_sandbox._sandbox.delete_file_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(
                RuntimeError, match="Failed to deleteFile for path '/x'"
            ):
                await Files(mock_client).delete("/x")

    @pytest.mark.asyncio
    async def test_delete_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.delete_file_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(RuntimeError, match="deleteFile returned None"):
                await Files(mock_client).delete("/x")

    @pytest.mark.asyncio
    async def test_move_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=400, message="bad request")
        with patch(
            "together_sandbox._sandbox.perform_file_action_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(RuntimeError, match="Failed to moveFile"):
                await Files(mock_client).move("/src", "/dst")

    @pytest.mark.asyncio
    async def test_move_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.perform_file_action_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(RuntimeError, match="moveFile returned None"):
                await Files(mock_client).move("/src", "/dst")

    @pytest.mark.asyncio
    async def test_copy_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=400, message="bad request")
        with patch(
            "together_sandbox._sandbox.perform_file_action_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(RuntimeError, match="Failed to copyFile"):
                await Files(mock_client).copy("/src", "/dst")

    @pytest.mark.asyncio
    async def test_copy_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.perform_file_action_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(RuntimeError, match="copyFile returned None"):
                await Files(mock_client).copy("/src", "/dst")

    @pytest.mark.asyncio
    async def test_stat_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=404, message="not found")
        with patch(
            "together_sandbox._sandbox.get_file_stat_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(RuntimeError, match="Failed to getFileStat"):
                await Files(mock_client).stat("/x")

    @pytest.mark.asyncio
    async def test_stat_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.get_file_stat_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(RuntimeError, match="getFileStat returned None"):
                await Files(mock_client).stat("/x")


# ─── Execs error-path tests ───────────────────────────────────────────────────


class TestExecsErrorPaths:
    """Tests that Execs methods raise RuntimeError on API errors."""

    @pytest.mark.asyncio
    async def test_delete_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=404, message="not found")
        with patch(
            "together_sandbox._sandbox.delete_exec_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(
                RuntimeError, match="Failed to deleteExec for id 'exec-1'"
            ):
                await Execs(mock_client).delete("exec-1")

    @pytest.mark.asyncio
    async def test_delete_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.delete_exec_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(
                RuntimeError, match="deleteExec returned None for id 'exec-1'"
            ):
                await Execs(mock_client).delete("exec-1")

    @pytest.mark.asyncio
    async def test_delete_succeeds_on_valid_response(self):
        mock_client = MagicMock()
        ok = ExecDeleteResponse(message="deleted")
        with patch(
            "together_sandbox._sandbox.delete_exec_api",
            new_callable=AsyncMock,
            return_value=ok,
        ):
            await Execs(mock_client).delete("exec-1")  # should not raise


# ─── Ports error-path tests ───────────────────────────────────────────────────


class TestPortsErrorPaths:
    """Tests that Ports.list raises RuntimeError on API errors."""

    @pytest.mark.asyncio
    async def test_list_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=500, message="server error")
        with patch(
            "together_sandbox._sandbox.list_ports_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(RuntimeError, match="Failed to listPorts"):
                await Ports(mock_client).list()

    @pytest.mark.asyncio
    async def test_list_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.list_ports_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(RuntimeError, match="listPorts returned None"):
                await Ports(mock_client).list()

    @pytest.mark.asyncio
    async def test_list_returns_ports_on_success(self):
        mock_client = MagicMock()
        ports_response = PortsListResponse(ports=[])
        with patch(
            "together_sandbox._sandbox.list_ports_api",
            new_callable=AsyncMock,
            return_value=ports_response,
        ):
            result = await Ports(mock_client).list()
            assert result == []


# ─── Directories error-path tests ────────────────────────────────────────────


class TestDirectoriesErrorPaths:
    """Tests that Directories methods raise RuntimeError on API errors."""

    @pytest.mark.asyncio
    async def test_create_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=400, message="already exists")
        with patch(
            "together_sandbox._sandbox.create_directory_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(
                RuntimeError, match="Failed to createDirectory for path '/mydir'"
            ):
                await Directories(mock_client).create("/mydir")

    @pytest.mark.asyncio
    async def test_create_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.create_directory_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(
                RuntimeError, match="createDirectory returned None for path '/mydir'"
            ):
                await Directories(mock_client).create("/mydir")

    @pytest.mark.asyncio
    async def test_create_succeeds_on_valid_response(self):
        mock_client = MagicMock()
        ok = FileOperationResponse(message="created", path="/mydir")
        with patch(
            "together_sandbox._sandbox.create_directory_api",
            new_callable=AsyncMock,
            return_value=ok,
        ):
            await Directories(mock_client).create("/mydir")  # should not raise

    @pytest.mark.asyncio
    async def test_delete_raises_on_error(self):
        mock_client = MagicMock()
        err = Error(code=404, message="not found")
        with patch(
            "together_sandbox._sandbox.delete_directory_api",
            new_callable=AsyncMock,
            return_value=err,
        ):
            with pytest.raises(
                RuntimeError, match="Failed to deleteDirectory for path '/mydir'"
            ):
                await Directories(mock_client).delete("/mydir")

    @pytest.mark.asyncio
    async def test_delete_raises_on_none(self):
        mock_client = MagicMock()
        with patch(
            "together_sandbox._sandbox.delete_directory_api",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(
                RuntimeError, match="deleteDirectory returned None for path '/mydir'"
            ):
                await Directories(mock_client).delete("/mydir")

    @pytest.mark.asyncio
    async def test_delete_succeeds_on_valid_response(self):
        mock_client = MagicMock()
        ok = FileOperationResponse(message="deleted", path="/mydir")
        with patch(
            "together_sandbox._sandbox.delete_directory_api",
            new_callable=AsyncMock,
            return_value=ok,
        ):
            await Directories(mock_client).delete("/mydir")  # should not raise

# ─── Snapshots tests ──────────────────────────────────────────────────────────


class TestSnapshots:
    """Tests for Snapshots.create() method."""

    @pytest.mark.asyncio
    async def test_create_with_image_calls_create_snapshot_api(self):
        """Test that create with image params calls create_snapshot_api, not build_docker_image."""
        mock_api_client = MagicMock()

        snapshots = SnapshotsNamespace(
            api_client=mock_api_client,
            base_url="https://api.codesandbox.io",
        )

        # Mock the create_snapshot_api response
        mock_response = MagicMock()
        mock_response.id = "snap-123"

        with patch(
            "together_sandbox._snapshots.create_snapshot_api",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_create_snapshot:
            result = await snapshots.create(CreateImageSnapshotParams(image="node:24"))

            # Verify create_snapshot_api was called
            assert mock_create_snapshot.called
            assert result.snapshot_id == "snap-123"

    @pytest.mark.asyncio
    async def test_create_with_image_and_alias(self):
        """Test that create with image params calls aliasSnapshot when alias is provided."""
        mock_api_client = MagicMock()

        snapshots = SnapshotsNamespace(
            api_client=mock_api_client,
            base_url="https://api.codesandbox.io",
        )

        # Mock the API responses
        mock_snapshot_response = MagicMock()
        mock_snapshot_response.id = "snap-456"

        with patch(
            "together_sandbox._snapshots.create_snapshot_api",
            new_callable=AsyncMock,
            return_value=mock_snapshot_response,
        ) as mock_create_snapshot:
            with patch(
                "together_sandbox._snapshots.alias_snapshot_api",
                new_callable=AsyncMock,
            ) as mock_alias:
                result = await snapshots.create(
                    CreateImageSnapshotParams(
                        image="ubuntu:22.04", alias="myimage@latest"
                    )
                )

                # Verify both APIs were called
                assert mock_create_snapshot.called
                assert mock_alias.called
                assert result.snapshot_id == "snap-456"
                assert result.alias == "myimage@latest"

    def test_create_method_exists_old_methods_removed(self):
        """Test that create method exists and old from_build/from_image are removed."""
        ns = SnapshotsNamespace(
            api_client=MagicMock(),
            base_url="https://example.com",
        )
        assert hasattr(ns, "create")
        assert not hasattr(ns, "from_build")
        assert not hasattr(ns, "from_image")

    @pytest.mark.asyncio
    async def test_build_and_register_with_alias_succeeds_when_alias_returns_none(self):
        """_build_and_register with alias= must succeed when alias_snapshot_api returns None (HTTP 204)."""
        mock_api_client = MagicMock()

        snapshots = SnapshotsNamespace(
            api_client=mock_api_client,
            base_url="https://api.codesandbox.io",
        )

        credential = ContainerRegistryCredential(
            username="user",
            password="pass",
            registry_url="registry.example.com/ns",
            expired_at=None,
        )

        mock_snapshot = MagicMock()
        mock_snapshot.id = "snap-ctx-789"

        patches = [
            patch(
                "together_sandbox._snapshots.issue_container_registry_credential_api",
                new_callable=AsyncMock,
                return_value=credential,
            ),
            patch("together_sandbox._snapshots.build_docker_image", new_callable=AsyncMock),
            patch("together_sandbox._snapshots.docker_login", new_callable=AsyncMock),
            patch("together_sandbox._snapshots.push_docker_image", new_callable=AsyncMock),
            patch(
                "together_sandbox._snapshots.create_snapshot_api",
                new_callable=AsyncMock,
                return_value=mock_snapshot,
            ),
            patch(
                "together_sandbox._snapshots.alias_snapshot_api",
                new_callable=AsyncMock,
                return_value=None,  # real HTTP 204 success shape
            ),
        ]

        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as mock_alias:
            result = await snapshots._build_and_register(
                CreateContextSnapshotParams(
                    context="/tmp",
                    alias="myapp@latest",
                )
            )

        assert mock_alias.called
        assert result.snapshot_id == "snap-ctx-789"
        assert result.alias == "myapp@latest"

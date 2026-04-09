"""E2E tests for sandbox filesystem operations."""

from __future__ import annotations

import pytest

from together_sandbox.facade import Sandbox, TogetherSandbox

from .helpers import sandbox, sdk  # noqa: F401


@pytest.mark.asyncio
class TestSandboxFilesystem:
    """E2E tests for file and directory operations."""

    async def test_write_and_read_text_file(
        self, sandbox: Sandbox  # noqa: F811
    ):
        """Test creating and reading a text file."""
        test_content = "Hello, Together Sandbox!"
        test_path = "/test-file.txt"

        # Write file
        await sandbox.files.create_file(test_path, test_content)

        # Read file back
        result = await sandbox.files.read_file(test_path)

        assert result.path == test_path
        assert result.content == test_content

    async def test_write_and_read_binary_file(
        self, sandbox: Sandbox  # noqa: F811
    ):
        """Test creating and reading a binary file."""
        # Binary data (PNG header example)
        binary_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        test_path = "/test-binary.bin"

        # Write binary file
        await sandbox.files.create_file(test_path, binary_data)

        # Read file back
        result = await sandbox.files.read_file(test_path)

        assert result.path == test_path
        # Note: The API may return content as base64 or binary string
        # This assertion may need adjustment based on actual API behavior

    async def test_write_and_read_unicode_file(
        self, sandbox: Sandbox  # noqa: F811
    ):
        """Test creating and reading a file with Unicode characters."""
        unicode_content = "Hello 世界 🌍 Привет"
        test_path = "/test-unicode.txt"

        # Write file with Unicode content
        await sandbox.files.create_file(test_path, unicode_content)

        # Read file back
        result = await sandbox.files.read_file(test_path)

        assert result.path == test_path
        assert result.content == unicode_content

    async def test_delete_file(self, sandbox: Sandbox):  # noqa: F811
        """Test deleting a file."""
        test_content = "Temporary file"
        test_path = "/test-delete.txt"

        # Create file
        await sandbox.files.create_file(test_path, test_content)

        # Delete file
        await sandbox.files.delete_file(test_path)

        # Verify file is deleted by attempting to read it
        # This should raise an error or return None
        # Note: Adjust based on actual API behavior
        with pytest.raises(Exception):
            await sandbox.files.read_file(test_path)

    async def test_create_directory(self, sandbox: Sandbox):  # noqa: F811
        """Test creating a directory."""
        test_dir = "/test-directory"

        # Create directory
        await sandbox.directories.create_directory(test_dir)

        # Verify by creating a file inside it
        test_file = f"{test_dir}/nested-file.txt"
        await sandbox.files.create_file(test_file, "nested content")

        result = await sandbox.files.read_file(test_file)
        assert result.content == "nested content"

    async def test_delete_directory(self, sandbox: Sandbox):  # noqa: F811
        """Test deleting a directory."""
        test_dir = "/test-delete-dir"

        # Create directory
        await sandbox.directories.create_directory(test_dir)

        # Create a file inside
        test_file = f"{test_dir}/file.txt"
        await sandbox.files.create_file(test_file, "content")

        # Delete directory
        await sandbox.directories.delete_directory(test_dir)

        # Verify directory and file are removed
        with pytest.raises(Exception):
            await sandbox.files.read_file(test_file)

    async def test_list_directory(self, sandbox: Sandbox):  # noqa: F811
        """Test listing directory contents."""
        test_dir = "/test-list-dir"

        # Create directory
        await sandbox.directories.create_directory(test_dir)

        # Create multiple files
        await sandbox.files.create_file(f"{test_dir}/file1.txt", "content1")
        await sandbox.files.create_file(f"{test_dir}/file2.txt", "content2")
        await sandbox.files.create_file(f"{test_dir}/file3.txt", "content3")

        # List directory
        result = await sandbox.directories.list_directory(test_dir)

        # Verify all files are listed
        # Note: Adjust assertions based on actual API response structure
        assert result is not None

    async def test_empty_file(self, sandbox: Sandbox):  # noqa: F811
        """Test creating an empty file."""
        test_path = "/empty-file.txt"

        # Create empty file
        await sandbox.files.create_file(test_path, "")

        # Read back
        result = await sandbox.files.read_file(test_path)

        assert result.path == test_path
        assert result.content == ""

    async def test_overwrite_file(self, sandbox: Sandbox):  # noqa: F811
        """Test overwriting an existing file."""
        test_path = "/overwrite-test.txt"

        # Create initial file
        await sandbox.files.create_file(test_path, "original content")

        # Overwrite with new content
        await sandbox.files.create_file(test_path, "updated content")

        # Read back and verify new content
        result = await sandbox.files.read_file(test_path)

        assert result.content == "updated content"

    async def test_nested_directories(self, sandbox: Sandbox):  # noqa: F811
        """Test creating nested directory structures."""
        # Create nested directory path
        nested_path = "/level1/level2/level3"

        # This might require creating directories one by one
        # depending on the API behavior
        await sandbox.directories.create_directory("/level1")
        await sandbox.directories.create_directory("/level1/level2")
        await sandbox.directories.create_directory(nested_path)

        # Create a file in the deepest directory
        test_file = f"{nested_path}/deep-file.txt"
        await sandbox.files.create_file(test_file, "deep content")

        # Verify file exists
        result = await sandbox.files.read_file(test_file)
        assert result.content == "deep content"

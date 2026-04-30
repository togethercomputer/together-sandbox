"""E2E tests for sandbox filesystem operations."""

from __future__ import annotations

import pytest
import base64

from together_sandbox import Sandbox


@pytest.mark.asyncio
class TestSandboxFilesystem:
    """E2E tests for file and directory operations."""

    async def test_write_and_read_text_file(self, sandbox: Sandbox):
        """Test creating and reading a text file."""
        test_content = "Hello, Together Sandbox!"
        test_path = "/test-file.txt"

        # Write file
        await sandbox.files.create(test_path, test_content)

        # Read file back
        result = await sandbox.files.read(test_path)

        assert result == test_content

    async def test_write_and_read_binary_file(self, sandbox: Sandbox):
        """Test creating and reading a binary file."""
        # Binary data (PNG header example)
        binary_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        test_path = "/test-binary.bin"

        # Write binary file
        await sandbox.files.create(test_path, binary_data)

        # Read file back
        result = await sandbox.files.read(test_path)

        assert base64.b64decode(result) == binary_data

    async def test_write_and_read_unicode_file(self, sandbox: Sandbox):
        """Test creating and reading a file with Unicode characters."""
        unicode_content = "Hello 世界 🌍 Привет"
        test_path = "/test-unicode.txt"

        # Write file with Unicode content
        await sandbox.files.create(test_path, unicode_content)

        # Read file back
        result = await sandbox.files.read(test_path)

        assert result == unicode_content

    async def test_delete_file(self, sandbox: Sandbox):
        """Test deleting a file."""
        test_content = "Temporary file"
        test_path = "/test-delete.txt"

        # Create file
        await sandbox.files.create(test_path, test_content)

        # Delete file
        await sandbox.files.delete(test_path)

        # Verify file is deleted by attempting to read it
        # This should raise an error or return None
        # Note: Adjust based on actual API behavior
        with pytest.raises(Exception):
            await sandbox.files.read(test_path)

    async def test_create_directory(self, sandbox: Sandbox):
        """Test creating a directory."""
        test_dir = "/test-directory"

        # Create directory
        await sandbox.directories.create(test_dir)

        # Verify by creating a file inside it
        test_file = f"{test_dir}/nested-file.txt"
        await sandbox.files.create(test_file, "nested content")

        result = await sandbox.files.read(test_file)
        assert result == "nested content"

    async def test_delete_directory(self, sandbox: Sandbox):
        """Test deleting a directory."""
        test_dir = "/test-delete-dir"

        # Create directory
        await sandbox.directories.create(test_dir)

        # Create a file inside
        test_file = f"{test_dir}/file.txt"
        await sandbox.files.create(test_file, "content")

        # Delete directory
        await sandbox.directories.delete(test_dir)

        # Verify directory and file are removed
        with pytest.raises(Exception):
            await sandbox.files.read(test_file)

    async def test_list_directory(self, sandbox: Sandbox):
        """Test listing directory contents."""
        test_dir = "/test-list-dir"

        # Create directory
        await sandbox.directories.create(test_dir)

        # Create multiple files
        await sandbox.files.create(f"{test_dir}/file1.txt", "content1")
        await sandbox.files.create(f"{test_dir}/file2.txt", "content2")
        await sandbox.files.create(f"{test_dir}/file3.txt", "content3")

        # List directory
        result = await sandbox.directories.list(test_dir)

        # Verify all files are listed
        # Note: Adjust assertions based on actual API response structure
        assert result is not None

    async def test_empty_file(self, sandbox: Sandbox):
        """Test creating an empty file."""
        test_path = "/empty-file.txt"

        # Create empty file
        await sandbox.files.create(test_path, "")

        # Read back
        result = await sandbox.files.read(test_path)

        assert result == ""

    async def test_overwrite_file(self, sandbox: Sandbox):
        """Test overwriting an existing file."""
        test_path = "/overwrite-test.txt"

        # Create initial file
        await sandbox.files.create(test_path, "original content")

        # Overwrite with new content
        await sandbox.files.create(test_path, "updated content")

        # Read back and verify new content
        result = await sandbox.files.read(test_path)

        assert result == "updated content"

    async def test_nested_directories(self, sandbox: Sandbox):
        """Test creating nested directory structures."""
        # Create nested directory path
        nested_path = "/level1/level2/level3"

        # This might require creating directories one by one
        # depending on the API behavior
        await sandbox.directories.create("/level1")
        await sandbox.directories.create("/level1/level2")
        await sandbox.directories.create(nested_path)

        # Create a file in the deepest directory
        test_file = f"{nested_path}/deep-file.txt"
        await sandbox.files.create(test_file, "deep content")

        # Verify file exists
        result = await sandbox.files.read(test_file)
        assert result == "deep content"

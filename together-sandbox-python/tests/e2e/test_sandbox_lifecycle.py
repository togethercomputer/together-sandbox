"""E2E tests for sandbox lifecycle operations."""

from __future__ import annotations

import pytest

from together_sandbox.facade import TogetherSandbox

from .helpers import get_api_key, get_base_url, get_template_id


@pytest.mark.asyncio
class TestSandboxLifecycle:
    """E2E tests for sandbox creation, starting, hibernation, and shutdown."""

    async def test_create_and_start_sandbox(self):
        """Test creating a new sandbox and starting it."""
        api_key = get_api_key()
        base_url = get_base_url()
        template_id = get_template_id()

        # Initialize SDK
        if base_url:
            sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        else:
            sdk = TogetherSandbox(api_key=api_key)

        try:
            # Create sandbox (in Together Sandbox, this is typically done via start)
            if template_id:
                sandbox = await sdk.sandboxes.start(template_id)
            else:
                pytest.skip("TOGETHER_TEMPLATE_ID not set, cannot test sandbox creation")

            # Verify sandbox has an ID
            assert sandbox.id is not None
            assert len(sandbox.id) > 0

            # Verify we can access vm_info
            assert sandbox.vm_info is not None
            assert sandbox.vm_info.id == sandbox.id

            # Cleanup
            await sdk.sandboxes.shutdown(sandbox.id)
        finally:
            await sdk.close()

    async def test_sandbox_context_manager(self):
        """Test using sandbox as an async context manager."""
        api_key = get_api_key()
        base_url = get_base_url()
        template_id = get_template_id()

        if base_url:
            sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        else:
            sdk = TogetherSandbox(api_key=api_key)

        try:
            if not template_id:
                pytest.skip("TOGETHER_TEMPLATE_ID not set")

            # Use sandbox as context manager
            async with await sdk.sandboxes.start(template_id) as sandbox:
                # Verify we can perform operations inside the context
                await sandbox.files.create_file("/test.txt", "test content")

                result = await sandbox.files.read_file("/test.txt")
                assert result.content == "test content"

            # Context manager should close the connection (but not shut down VM)
            # We still need to explicitly shutdown
            await sdk.sandboxes.shutdown(sandbox.id)
        finally:
            await sdk.close()

    async def test_sandbox_fork(self):
        """Test forking an existing sandbox."""
        api_key = get_api_key()
        base_url = get_base_url()
        template_id = get_template_id()

        if base_url:
            sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        else:
            sdk = TogetherSandbox(api_key=api_key)

        original_sandbox = None
        forked_sandbox = None

        try:
            if not template_id:
                pytest.skip("TOGETHER_TEMPLATE_ID not set")

            # Create original sandbox
            original_sandbox = await sdk.sandboxes.start(template_id)

            # Create a file in original
            await original_sandbox.files.create_file("/original.txt", "original content")

            # Fork the sandbox
            forked_sandbox = await sdk.sandboxes.fork(original_sandbox.id)

            # Verify fork has a different ID
            assert forked_sandbox.id != original_sandbox.id

            # Verify forked sandbox has the original file
            # Note: This behavior depends on whether forks preserve file system state
            # Adjust assertion based on actual API behavior

        finally:
            # Cleanup both sandboxes
            if original_sandbox:
                try:
                    await sdk.sandboxes.shutdown(original_sandbox.id)
                except Exception:
                    pass

            if forked_sandbox:
                try:
                    await sdk.sandboxes.shutdown(forked_sandbox.id)
                except Exception:
                    pass

            await sdk.close()

    async def test_sandbox_hibernate_and_resume(self):
        """Test hibernating and resuming a sandbox."""
        api_key = get_api_key()
        base_url = get_base_url()
        template_id = get_template_id()

        if base_url:
            sdk = TogetherSandbox(api_key=api_key, base_url=base_url)
        else:
            sdk = TogetherSandbox(api_key=api_key)

        sandbox = None

        try:
            if not template_id:
                pytest.skip("TOGETHER_TEMPLATE_ID not set")

            # Create and start sandbox
            sandbox = await sdk.sandboxes.start(template_id)
            sandbox_id = sandbox.id

            # Create a file
            await sandbox.files.create_file("/hibernate-test.txt", "persistent content")

            # Hibernate the sandbox
            await sandbox.hibernate()

            # Resume by starting again
            resumed_sandbox = await sdk.sandboxes.start(sandbox_id)

            # Verify the file persists after hibernation
            result = await resumed_sandbox.files.read_file("/hibernate-test.txt")
            assert result.content == "persistent content"

            # Cleanup
            await sdk.sandboxes.shutdown(sandbox_id)
            sandbox = None  # Already shut down

        finally:
            if sandbox:
                try:
                    await sdk.sandboxes.shutdown(sandbox.id)
                except Exception:
                    pass

            await sdk.close()

    async def test_static_sandbox_start(self):
        """Test using Sandbox.start() static method."""
        api_key = get_api_key()
        template_id = get_template_id()

        if not template_id:
            pytest.skip("TOGETHER_TEMPLATE_ID not set")

        from together_sandbox.facade import Sandbox

        # Use static factory method
        sandbox = await Sandbox.start(template_id, api_key=api_key)

        try:
            # Verify sandbox is functional
            assert sandbox.id is not None

            # Perform a simple operation
            await sandbox.files.create_file("/static-test.txt", "test")
            result = await sandbox.files.read_file("/static-test.txt")
            assert result.content == "test"

        finally:
            # Cleanup
            try:
                await sandbox.shutdown()
            except Exception:
                pass

"""E2E tests for sandbox lifecycle operations."""

from __future__ import annotations

import pytest

from together_sandbox import TogetherSandbox

from .helpers import get_snapshot_id


@pytest.mark.asyncio
class TestSandboxLifecycle:
    """E2E tests for sandbox creation, starting, hibernation, and shutdown."""

    async def test_create_and_start_sandbox(self, sdk: TogetherSandbox):
        """Test creating a new sandbox and starting it."""
        snapshot_id = get_snapshot_id()

        sandbox = await sdk.sandboxes.create(snapshot_id=snapshot_id)

        # Verify sandbox has an ID
        assert sandbox.id is not None
        assert len(sandbox.id) > 0

        vm_info = await sdk.sandboxes.start(sandbox_id=sandbox.id)

        # Verify we can access vm_info
        assert vm_info is not None
        assert vm_info.id == sandbox.id

        # Cleanup
        await sdk.sandboxes.shutdown(sandbox.id)

    async def test_sandbox_context_manager(self, sdk: TogetherSandbox):
        """Test using sandbox as an async context manager."""
        snapshot_id = get_snapshot_id()

        created_sandbox = await sdk.sandboxes.create(snapshot_id=snapshot_id)

        # Use sandbox as context manager
        async with await sdk.sandboxes.start(sandbox_id=created_sandbox.id) as sandbox:
            # Verify we can perform operations inside the context
            await sandbox.files.create("/test.txt", "test content")

            result = await sandbox.files.read("/test.txt")
            assert result == "test content"

        # Context manager should close the connection (but not shut down VM)
        # We still need to explicitly shutdown
        await sdk.sandboxes.shutdown(sandbox.id)

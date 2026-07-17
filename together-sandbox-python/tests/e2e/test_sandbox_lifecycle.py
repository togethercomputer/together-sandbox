"""E2E tests for sandbox lifecycle operations."""

from __future__ import annotations

import pytest

from together_sandbox import TogetherSandbox

from .helpers import get_snapshot_id


@pytest.mark.asyncio
class TestSandboxLifecycle:
    """E2E tests for sandbox creation, starting, hibernation, and shutdown."""

    async def test_create_sandbox(self, sdk: TogetherSandbox):
        """Test creating a sandbox — returns a connected, running Sandbox."""
        snapshot_id = get_snapshot_id()

        sandbox = await sdk.sandboxes.create(snapshot_id=snapshot_id)

        assert sandbox.id is not None
        assert len(sandbox.id) > 0

        await sdk.sandboxes.shutdown(sandbox.id)

    async def test_sandbox_context_manager(self, sdk: TogetherSandbox):
        """Test using sandbox as an async context manager."""
        snapshot_id = get_snapshot_id()

        async with await sdk.sandboxes.create(snapshot_id=snapshot_id) as sandbox:
            await sandbox.files.create("/test.txt", "test content")

            result = await sandbox.files.read("/test.txt")
            assert result == "test content"

        # Context manager closes the HTTP connection but does not shut down the VM.
        await sdk.sandboxes.shutdown(sandbox.id)

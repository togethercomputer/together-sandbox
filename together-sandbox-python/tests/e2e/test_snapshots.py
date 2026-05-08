from __future__ import annotations

import os
import pathlib
import tempfile

import pytest
import uuid

from together_sandbox._snapshots import (
    CreateSnapshotResult,
    CreateContextSnapshotParams,
)
from together_sandbox._together_sandbox import TogetherSandbox

# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def docker_context() -> str:
    with tempfile.TemporaryDirectory(prefix="e2e-snapshot-") as d:
        (pathlib.Path(d) / "Dockerfile").write_text("FROM alpine:latest\n")
        yield d


# ─── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestSnapshots:
    """End-to-end tests for snapshot creation."""

    @pytest.mark.timeout(300)
    async def test_create_from_context_with_alias(self, docker_context: str) -> None:
        """Test snapshot creation from Docker build with alias."""
        sdk = TogetherSandbox(api_key=os.environ["CSB_API_KEY"])
        alias = f"e2e-build-{uuid.uuid4().hex[:8]}"
        result: CreateSnapshotResult | None = None
        try:
            result = await sdk.snapshots.create(
                CreateContextSnapshotParams(context=docker_context, alias=alias)
            )
            assert result.snapshot_id
            assert isinstance(result.snapshot_id, str)
            assert result.alias is not None
            assert "e2e-build" in result.alias
        finally:
            if result is not None:
                await sdk.snapshots.delete_by_id(result.snapshot_id)

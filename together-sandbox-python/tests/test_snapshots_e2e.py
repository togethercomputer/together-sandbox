from __future__ import annotations

import os
import pathlib
import tempfile

import pytest

from together_sandbox._snapshots import BuildSnapshotParams, CreateSnapshotResult
from together_sandbox._together_sandbox import TogetherSandbox

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("CSB_API_KEY"),
        reason="CSB_API_KEY not set",
    ),
]


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def docker_context() -> str:
    with tempfile.TemporaryDirectory(prefix="e2e-snapshot-") as d:
        (pathlib.Path(d) / "Dockerfile").write_text("FROM alpine:latest\n")
        yield d


# ─── Tests ────────────────────────────────────────────────────────────────────


class TestSnapshots:
    """End-to-end tests for snapshot creation."""

    @pytest.mark.timeout(300)
    async def test_from_build_with_alias(self, docker_context: str) -> None:
        """Test snapshot creation from Docker build with alias."""
        sdk = TogetherSandbox(api_key=os.environ["CSB_API_KEY"])
        result: CreateSnapshotResult = await sdk.snapshots.from_build(
            docker_context,
            BuildSnapshotParams(alias="e2e-build"),
        )
        assert result.snapshot_id
        assert isinstance(result.snapshot_id, str)
        assert result.alias is not None
        assert "e2e-build" in result.alias
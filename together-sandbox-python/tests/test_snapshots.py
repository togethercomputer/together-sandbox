"""Tests for snapshot operations."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from uuid import UUID
from datetime import datetime

from together_sandbox._snapshots import SnapshotsNamespace
from together_sandbox.api.models.snapshot import Snapshot
from together_sandbox.api.models.snapshot_type import SnapshotType
from together_sandbox.api.models.error import Error
from together_sandbox.api.models.error_type import ErrorType


@pytest.mark.asyncio
class TestSnapshotsNamespace:
    """Tests for SnapshotsNamespace.get_by_alias()."""

    async def test_get_snapshot_by_alias(self):
        """Test retrieving snapshot information by alias."""
        # Create mock API client
        mock_api_client = MagicMock()

        # Create a mock snapshot response
        mock_snapshot = Snapshot(
            field_type_=SnapshotType.SNAPSHOT,
            id=UUID("12345678-1234-5678-1234-567812345678"),
            byte_size=1024000,
            protected=False,
            optimized=True,
            includes_memory_snapshot=False,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            optimized_at=datetime(2024, 1, 1, 13, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 30, 0),
        )

        # Create snapshots namespace
        snapshots = SnapshotsNamespace(
            api_client=mock_api_client,
            api_key="test-api-key",
            base_url="https://api.codesandbox.io",
        )

        # Mock the get_snapshot_by_alias_api function
        with pytest.MonkeyPatch.context() as mp:

            async def mock_get_snapshot_by_alias_api(alias: str, *, client):
                return mock_snapshot

            # Patch the imported function in _snapshots module
            mp.setattr(
                "together_sandbox._snapshots.get_snapshot_by_alias_api",
                mock_get_snapshot_by_alias_api,
            )

            # Call the method
            result = await snapshots.get_by_alias("my-app@latest")

            # Verify result
            assert result.id == UUID("12345678-1234-5678-1234-567812345678")
            assert result.byte_size == 1024000
            assert result.optimized is True
            assert result.includes_memory_snapshot is False

    async def test_get_snapshot_strips_leading_at_symbol(self):
        """Test that get_snapshot strips leading @ from alias."""
        mock_api_client = MagicMock()
        mock_snapshot = Snapshot(
            field_type_=SnapshotType.SNAPSHOT,
            id=UUID("12345678-1234-5678-1234-567812345678"),
            byte_size=1024000,
            protected=False,
            optimized=True,
            includes_memory_snapshot=False,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            optimized_at=None,
            updated_at=datetime(2024, 1, 1, 12, 30, 0),
        )

        snapshots = SnapshotsNamespace(
            api_client=mock_api_client,
            api_key="test-api-key",
            base_url="https://api.codesandbox.io",
        )

        received_alias = None

        with pytest.MonkeyPatch.context() as mp:

            async def mock_get_snapshot_by_alias_api(alias: str, *, client):
                nonlocal received_alias
                received_alias = alias
                return mock_snapshot

            mp.setattr(
                "together_sandbox._snapshots.get_snapshot_by_alias_api",
                mock_get_snapshot_by_alias_api,
            )

            # Call with @ prefix
            await snapshots.get_by_alias("@my-app@latest")

            # Verify @ was stripped
            assert received_alias == "my-app@latest"

    async def test_get_snapshot_not_found_raises_error(self):
        """Test that get_snapshot raises RuntimeError when API returns None."""
        mock_api_client = MagicMock()

        snapshots = SnapshotsNamespace(
            api_client=mock_api_client,
            api_key="test-api-key",
            base_url="https://api.codesandbox.io",
        )

        with pytest.MonkeyPatch.context() as mp:

            async def mock_get_snapshot_by_alias_api(alias: str, *, client):
                return None  # Simulate unexpected response

            mp.setattr(
                "together_sandbox._snapshots.get_snapshot_by_alias_api",
                mock_get_snapshot_by_alias_api,
            )

            # Should raise RuntimeError with unexpected response message
            with pytest.raises(RuntimeError, match="getSnapshotByAlias returned None"):
                await snapshots.get_by_alias("nonexistent@alias")

    async def test_get_snapshot_error_response_raises_error(self):
        """Test that get_snapshot raises RuntimeError when API returns Error."""
        mock_api_client = MagicMock()

        snapshots = SnapshotsNamespace(
            api_client=mock_api_client,
            api_key="test-api-key",
            base_url="https://api.codesandbox.io",
        )

        # Create a mock Error response (404)
        mock_error = Error(
            field_type_=ErrorType.ERROR,
            code="SNAPSHOT_NOT_FOUND",
            message="Snapshot with alias 'nonexistent@alias' not found",
            errors=[],
        )

        with pytest.MonkeyPatch.context() as mp:

            async def mock_get_snapshot_by_alias_api(alias: str, *, client):
                return mock_error  # Simulate API error response

            mp.setattr(
                "together_sandbox._snapshots.get_snapshot_by_alias_api",
                mock_get_snapshot_by_alias_api,
            )

            # Should raise RuntimeError with error details
            with pytest.raises(RuntimeError, match="SNAPSHOT_NOT_FOUND"):
                await snapshots.get_by_alias("nonexistent@alias")

            # Verify the error message contains both the message and code
            with pytest.raises(
                RuntimeError, match="Snapshot with alias 'nonexistent@alias' not found"
            ):
                await snapshots.get_by_alias("nonexistent@alias")

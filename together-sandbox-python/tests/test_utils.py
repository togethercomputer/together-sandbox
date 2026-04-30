"""Unit tests for the Together Sandbox unified facade."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from together_sandbox._sandbox import (
    _unwrap_or_raise,
)
from together_sandbox._sandboxes import _resolve_connection
from together_sandbox.sandbox.models.error import Error
from together_sandbox.api.models.sandbox import Sandbox as SandboxModel

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

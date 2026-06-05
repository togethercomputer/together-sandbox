"""Unit tests for the Together Sandbox unified facade."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
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

# ─── RetryConfig docstring integrity ──────────────────────────────────────────


class TestRetryConfigDocstring:
    def test_docstring_does_not_contain_stray_return_result(self):
        """RetryConfig.__doc__ must not contain the accidental 'return result' fragment."""
        from together_sandbox._utils import RetryConfig

        assert RetryConfig.__doc__ is not None
        assert "return result" not in RetryConfig.__doc__


# ─── Sandbox lifecycle method resolution ──────────────────────────────────────


class TestSandboxLifecycleMethods:
    """Guard against classmethods shadowing same-named instance methods.

    In Python, a ``@classmethod`` defined after an instance method of the same
    name silently replaces it in the class ``__dict__``.  If ``hibernate`` or
    ``shutdown`` resolves as a classmethod on ``Sandbox``, calling
    ``await sandbox.hibernate()`` on an instance raises ``TypeError`` because
    the classmethod expects ``sandbox_id`` as its first positional argument.
    """

    def test_hibernate_is_instance_method_not_classmethod(self):
        """Sandbox.hibernate must be a coroutine function, not a classmethod."""
        import inspect
        from together_sandbox._sandbox import Sandbox

        raw = inspect.getattr_static(Sandbox, "hibernate")
        assert not isinstance(raw, classmethod), (
            "Sandbox.hibernate resolved as a classmethod — it shadows the "
            "instance method and breaks await sandbox.hibernate()"
        )
        assert inspect.iscoroutinefunction(raw), (
            "Sandbox.hibernate must be an async instance method"
        )

    def test_shutdown_is_instance_method_not_classmethod(self):
        """Sandbox.shutdown must be a coroutine function, not a classmethod."""
        import inspect
        from together_sandbox._sandbox import Sandbox

        raw = inspect.getattr_static(Sandbox, "shutdown")
        assert not isinstance(raw, classmethod), (
            "Sandbox.shutdown resolved as a classmethod — it shadows the "
            "instance method and breaks await sandbox.shutdown()"
        )
        assert inspect.iscoroutinefunction(raw), (
            "Sandbox.shutdown must be an async instance method"
        )

    def test_hibernate_by_id_is_classmethod(self):
        """Sandbox.hibernate_by_id must be the classmethod factory."""
        import inspect
        from together_sandbox._sandbox import Sandbox

        raw = inspect.getattr_static(Sandbox, "hibernate_by_id")
        assert isinstance(raw, classmethod), (
            "Sandbox.hibernate_by_id must be a classmethod"
        )

    def test_shutdown_by_id_is_classmethod(self):
        """Sandbox.shutdown_by_id must be the classmethod factory."""
        import inspect
        from together_sandbox._sandbox import Sandbox

        raw = inspect.getattr_static(Sandbox, "shutdown_by_id")
        assert isinstance(raw, classmethod), (
            "Sandbox.shutdown_by_id must be a classmethod"
        )

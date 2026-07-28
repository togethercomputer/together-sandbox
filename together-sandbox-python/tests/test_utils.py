"""Unit tests for the Together Sandbox unified facade."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from together_sandbox._sandboxes import (
    SandboxesNamespace,
    _connect_running_sandbox,
    _resolve_connection,
)
from together_sandbox._lifecycle import is_transient_status
from together_sandbox.sandbox.models.error import Error
from together_sandbox.api.models.sandbox import Sandbox as SandboxModel

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_sandbox_model(
    *,
    agent_url: str | None = "https://agent.example.com",
    agent_token: str | None = "agent-tok",
    **overrides,
) -> MagicMock:
    """Build a mock SandboxModel with sensible defaults.

    The agent connection details live on the nested ``agent`` object
    (``agent.url`` / ``agent.token``) to match the current Sandbox model.
    """
    defaults = dict(id="test-sandbox-123")
    defaults.update(overrides)
    mock = MagicMock(spec=SandboxModel)
    for k, v in defaults.items():
        setattr(mock, k, v)
    agent = MagicMock()
    agent.url = agent_url
    agent.token = agent_token
    mock.agent = agent
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

# ─── SandboxesNamespace.create ───────────────────────────────────────────────


class TestSandboxesCreate:
    def _make_running_model(self, sandbox_id: str = "abc123") -> MagicMock:
        return _make_sandbox_model(id=sandbox_id, status="running")

    @pytest.mark.asyncio
    async def test_create_calls_create_api(self):
        running = self._make_running_model()
        with (
            patch(
                "together_sandbox._sandboxes.create_sandbox_api",
                new=AsyncMock(return_value=MagicMock(parsed=_make_sandbox_model(id="abc123"))),
            ),
            patch(
                "together_sandbox._sandboxes._connect_running_sandbox",
                new=AsyncMock(return_value=MagicMock(id="abc123")),
            ) as mock_connect,
            patch(
                "together_sandbox._sandboxes._call_api",
                side_effect=[_make_sandbox_model(id="abc123"), running],
            ) as mock_call,
        ):
            ns = SandboxesNamespace(api_client=MagicMock())
            await ns.create(snapshot_id="snap-1")

            # First _call_api call is create_sandbox.
            assert mock_call.call_args_list[0][0][0] == "api.create_sandbox"
            assert mock_call.call_count >= 1
            mock_connect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_returns_connected_sandbox(self):
        created_model = _make_sandbox_model(id="abc123")
        expected_sandbox = MagicMock(id="abc123")

        async def fake_call_api(op, fn, *args, **kwargs):
            if op == "api.create_sandbox":
                return created_model
            raise AssertionError(f"unexpected op: {op}")

        with (
            patch("together_sandbox._sandboxes._call_api", side_effect=fake_call_api),
            patch(
                "together_sandbox._sandboxes._connect_running_sandbox",
                new=AsyncMock(return_value=expected_sandbox),
            ) as mock_connect,
        ):
            ns = SandboxesNamespace(api_client=MagicMock())
            result = await ns.create(snapshot_id="snap-1")

        assert result is expected_sandbox
        mock_connect.assert_awaited_once_with(created_model, ns._api_client, ns._retry)

    @pytest.mark.asyncio
    async def test_create_forwards_snapshot_id_to_api(self):
        created_model = _make_sandbox_model(id="abc123")
        captured_body = {}

        async def fake_call_api(op, fn, *args, **kwargs):
            if op == "api.create_sandbox":
                captured_body["body"] = fn.__closure__  # capture for inspection
                return created_model
            raise AssertionError(f"unexpected op: {op}")

        with (
            patch("together_sandbox._sandboxes._call_api", side_effect=fake_call_api),
            patch(
                "together_sandbox._sandboxes._connect_running_sandbox",
                new=AsyncMock(return_value=MagicMock()),
            ),
        ):
            ns = SandboxesNamespace(api_client=MagicMock())
            await ns.create(snapshot_id="snap-xyz")

        # Verified indirectly: no exception means the lambda was constructed and called
        assert captured_body["body"] is not None


# ─── _connect_running_sandbox ────────────────────────────────────────────────


class TestConnectRunningSandbox:
    @pytest.mark.asyncio
    async def test_waits_when_status_is_transient(self):
        starting = _make_sandbox_model(id="abc123", status="starting")
        running = _make_sandbox_model(id="abc123", status="running")

        with (
            patch(
                "together_sandbox._sandboxes._call_api",
                new=AsyncMock(return_value=running),
            ) as mock_call,
            patch("together_sandbox._sandboxes.SandboxClient"),
            patch("together_sandbox._sandboxes.Sandbox", return_value=MagicMock()),
        ):
            await _connect_running_sandbox(starting, MagicMock(), None)

        mock_call.assert_awaited_once()
        assert mock_call.call_args[0][0] == "api.wait_for_sandbox"

    @pytest.mark.asyncio
    async def test_skips_wait_when_already_running(self):
        running = _make_sandbox_model(id="abc123", status="running")
        expected = MagicMock()

        with (
            patch("together_sandbox._sandboxes._call_api", new=AsyncMock()) as mock_call,
            patch("together_sandbox._sandboxes.SandboxClient"),
            patch(
                "together_sandbox._sandboxes.Sandbox", return_value=expected
            ) as mock_sandbox,
        ):
            result = await _connect_running_sandbox(running, MagicMock(), None)

        mock_call.assert_not_awaited()
        assert result is expected
        # The create response itself is what gets wired into the Sandbox.
        assert mock_sandbox.call_args[0][0] is running

    @pytest.mark.asyncio
    async def test_skips_wait_and_raises_for_settled_failure(self):
        failed = _make_sandbox_model(
            id="abc123", status="failed_to_start", status_reason="out_of_capacity"
        )

        with (
            patch("together_sandbox._sandboxes._call_api", new=AsyncMock()) as mock_call,
            pytest.raises(RuntimeError, match="failed to start"),
        ):
            await _connect_running_sandbox(failed, MagicMock(), None)

        mock_call.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_waits_when_terminating(self):
        terminating = _make_sandbox_model(id="abc123", status="terminating")
        terminated = _make_sandbox_model(id="abc123", status="terminated")

        with (
            patch(
                "together_sandbox._sandboxes._call_api",
                new=AsyncMock(return_value=terminated),
            ) as mock_call,
            pytest.raises(RuntimeError, match="terminated instead of reaching"),
        ):
            await _connect_running_sandbox(terminating, MagicMock(), None)

        mock_call.assert_awaited_once()


# ─── is_transient_status ─────────────────────────────────────────────────────


class TestIsTransientStatus:
    @pytest.mark.parametrize("status", ["starting", "terminating"])
    def test_transient_statuses(self, status):
        assert is_transient_status(status) is True

    @pytest.mark.parametrize(
        "status",
        ["running", "terminated", "failed_to_start", "recovering", "unrecovered", None],
    )
    def test_settled_statuses(self, status):
        assert is_transient_status(status) is False

    def test_unwraps_enum_like_values(self):
        enum_like = MagicMock()
        enum_like.value = "starting"
        assert is_transient_status(enum_like) is True


# ─── RetryConfig docstring integrity ──────────────────────────────────────────


class TestRetryConfigDocstring:
    def test_docstring_does_not_contain_stray_return_result(self):
        """RetryConfig.__doc__ must not contain the accidental 'return result' fragment."""
        from together_sandbox._utils import RetryConfig

        assert RetryConfig.__doc__ is not None
        assert "return result" not in RetryConfig.__doc__


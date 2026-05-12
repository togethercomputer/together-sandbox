"""Unit tests for the _call_api utility."""

from __future__ import annotations

from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from together_sandbox._utils import (
    RETRYABLE_STATUS_CODES,
    RetryConfig,
    RetryContext,
    _call_api,
)
from together_sandbox.api.models import Error as ApiError
from together_sandbox.api.types import Response
from together_sandbox.errors import HttpError
from together_sandbox.sandbox.models.error import Error as SandboxError

# ─── Helpers ─────────────────────────────────────────────────────────────────


def make_response(status: int, parsed) -> Response:
    """Build a mock Response with the given HTTP status and parsed value."""
    return Response(
        status_code=HTTPStatus(status),
        content=b"",
        headers={},
        parsed=parsed,
    )


def make_success_response(data=None) -> Response:
    """200 response with a success model (MagicMock by default)."""
    return make_response(200, data if data is not None else MagicMock())


def make_error_response(status: int) -> Response:
    """Response with None parsed — undocumented status (e.g. 500, 503)."""
    return make_response(status, None)


def make_api_error_response(
    status: int, message: str = "error", code: str = "ERROR"
) -> Response:
    """Response with an ApiError model — documented error status (e.g. 400, 404)."""
    return make_response(status, ApiError(message=message, code=code, errors=[]))


# ─── Success path ─────────────────────────────────────────────────────────────


class TestCallApiSuccess:
    @pytest.mark.asyncio
    async def test_returns_parsed_on_first_attempt(self):
        data = MagicMock()
        fn = AsyncMock(return_value=make_success_response(data))

        result = await _call_api("testOp", fn)

        assert result is data
        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_call_on_retry_on_success(self):
        on_retry = MagicMock()
        fn = AsyncMock(return_value=make_success_response())

        with patch("together_sandbox._utils.asyncio.sleep"):
            await _call_api("testOp", fn, RetryConfig(on_retry=on_retry))

        on_retry.assert_not_called()


# ─── Default retry on HTTP status ────────────────────────────────────────────


class TestCallApiDefaultRetryHttpStatus:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", sorted(RETRYABLE_STATUS_CODES))
    async def test_retries_on_retryable_status(self, status: int):
        data = MagicMock()
        fn = AsyncMock(
            side_effect=[
                make_error_response(status),
                make_success_response(data),
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _call_api("testOp", fn)

        assert result is data
        assert fn.call_count == 2

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", [400, 401, 403, 404])
    async def test_does_not_retry_on_non_retryable_status(self, status: int):
        fn = AsyncMock(return_value=make_error_response(status))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn)

        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_exhausts_default_max_attempts_then_raises(self):
        fn = AsyncMock(return_value=make_error_response(500))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn)

        assert fn.call_count == 3  # default max_attempts=3

    @pytest.mark.asyncio
    async def test_fn_called_exactly_max_attempts_times(self):
        fn = AsyncMock(return_value=make_error_response(503))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn, RetryConfig(max_attempts=2))

        assert fn.call_count == 2


# ─── Default retry on connection error ───────────────────────────────────────


class TestCallApiDefaultRetryConnectionError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exc",
        [
            httpx.TimeoutException("timed out"),
            httpx.ConnectError("refused"),
            httpx.RemoteProtocolError("closed"),
        ],
    )
    async def test_retries_on_network_error(self, exc: Exception):
        data = MagicMock()
        fn = AsyncMock(side_effect=[exc, make_success_response(data)])

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _call_api("testOp", fn)

        assert result is data
        assert fn.call_count == 2

    @pytest.mark.asyncio
    async def test_wraps_network_error_into_http_error_after_max_attempts(self):
        fn = AsyncMock(side_effect=httpx.TimeoutException("timed out"))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(HttpError) as exc_info:
                await _call_api("testOp", fn, RetryConfig(max_attempts=2))

        assert exc_info.value.status == 0
        assert "timed out" in str(exc_info.value)
        # Original transport exception preserved on __cause__ for debugging.
        assert isinstance(exc_info.value.__cause__, httpx.TimeoutException)
        assert fn.call_count == 2


# ─── Error model in parsed ────────────────────────────────────────────────────


class TestCallApiErrorModel:
    @pytest.mark.asyncio
    async def test_raises_for_api_error_at_non_retryable_status(self):
        fn = AsyncMock(
            return_value=make_api_error_response(
                404, message="not found", code="NOT_FOUND"
            )
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError, match="testOp"):
                await _call_api("testOp", fn)

        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_message_includes_model_message_field(self):
        fn = AsyncMock(
            return_value=make_api_error_response(
                400, message="missing field", code="BAD_REQUEST"
            )
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError, match="missing field"):
                await _call_api("testOp", fn)

    @pytest.mark.asyncio
    async def test_retries_api_error_at_retryable_status(self):
        """An ApiError model at a retryable status code (e.g. 500) should still retry."""
        data = MagicMock()
        fn = AsyncMock(
            side_effect=[
                make_api_error_response(500, message="server error"),
                make_success_response(data),
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _call_api("testOp", fn)

        assert result is data
        assert fn.call_count == 2

    @pytest.mark.asyncio
    async def test_raises_for_sandbox_error_model(self):
        sandbox_err = SandboxError(message="exec failed", code=500)
        fn = AsyncMock(return_value=make_response(500, sandbox_err))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn, RetryConfig(max_attempts=1))

    @pytest.mark.asyncio
    async def test_error_message_includes_context(self):
        fn = AsyncMock(return_value=make_api_error_response(400, message="bad input"))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError, match="for sandbox 'abc'"):
                await _call_api("testOp", fn, context="for sandbox 'abc'")


# ─── should_retry override ────────────────────────────────────────────────────


class TestCallApiShouldRetry:
    @pytest.mark.asyncio
    async def test_returning_false_stops_immediately(self):
        should_retry = MagicMock(return_value=False)
        fn = AsyncMock(return_value=make_error_response(500))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn, RetryConfig(should_retry=should_retry))

        fn.assert_called_once()
        should_retry.assert_called_once()

    @pytest.mark.asyncio
    async def test_returning_true_retries_non_retryable_status(self):
        """True overrides the default — retries even on a normally non-retryable code."""
        should_retry = MagicMock(return_value=True)
        data = MagicMock()
        fn = AsyncMock(
            side_effect=[
                make_error_response(400),
                make_success_response(data),
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _call_api(
                "testOp", fn, RetryConfig(should_retry=should_retry)
            )

        assert result is data
        assert fn.call_count == 2

    @pytest.mark.asyncio
    async def test_returning_float_uses_it_as_delay(self):
        should_retry = MagicMock(return_value=2.5)
        on_retry = MagicMock()
        data = MagicMock()
        fn = AsyncMock(
            side_effect=[
                make_error_response(500),
                make_success_response(data),
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            await _call_api(
                "testOp",
                fn,
                RetryConfig(should_retry=should_retry, on_retry=on_retry),
            )

        ctx: RetryContext = on_retry.call_args[0][0]
        assert ctx.delay == 2.5

    @pytest.mark.asyncio
    async def test_called_with_correct_retry_context_shape(self):
        should_retry = MagicMock(return_value=False)
        fn = AsyncMock(return_value=make_error_response(503))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api("myOp", fn, RetryConfig(should_retry=should_retry))

        ctx: RetryContext = should_retry.call_args[0][0]
        assert ctx.operation == "myOp"
        assert ctx.attempt == 1
        assert ctx.status == 503
        assert isinstance(ctx.error, Exception)
        assert isinstance(ctx.delay, float)

    @pytest.mark.asyncio
    async def test_attempt_numbers_are_1_based(self):
        attempts_seen: list[int] = []

        def should_retry(ctx: RetryContext) -> bool:
            attempts_seen.append(ctx.attempt)
            return True

        fn = AsyncMock(return_value=make_error_response(500))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api(
                    "testOp", fn, RetryConfig(should_retry=should_retry, max_attempts=3)
                )

        # should_retry is called for attempts 1 and 2; attempt 3 is the final (no retry)
        assert attempts_seen == [1, 2]


# ─── on_retry callback ────────────────────────────────────────────────────────


class TestCallApiOnRetry:
    @pytest.mark.asyncio
    async def test_called_once_per_failed_attempt_not_on_final(self):
        on_retry = MagicMock()
        fn = AsyncMock(return_value=make_error_response(500))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api(
                    "testOp", fn, RetryConfig(on_retry=on_retry, max_attempts=3)
                )

        # 3 attempts → 2 retries → on_retry called twice (not on the final failure)
        assert on_retry.call_count == 2

    @pytest.mark.asyncio
    async def test_called_with_correct_1_based_attempt(self):
        on_retry = MagicMock()
        fn = AsyncMock(return_value=make_error_response(500))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api(
                    "testOp", fn, RetryConfig(on_retry=on_retry, max_attempts=3)
                )

        attempts = [c[0][0].attempt for c in on_retry.call_args_list]
        assert attempts == [1, 2]


# ─── Exponential backoff delay values ───────────────────────────────────────────────────


class TestCallApiBackoffDelay:
    @pytest.mark.asyncio
    async def test_backoff_delay_values_are_exponential(self):
        """Verify BASE_DELAY * 2^(attempt-1) with zero jitter.

        BASE_DELAY = 0.5s, JITTER = 0.25s, random.random() = 0.0
        attempt 1 → 0.5 * 2° + 0.0 = 0.5
        attempt 2 → 0.5 * 2¹ + 0.0 = 1.0
        """
        sleep_calls: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleep_calls.append(seconds)

        fn = AsyncMock(return_value=make_error_response(500))

        with (
            patch("together_sandbox._utils.asyncio.sleep", side_effect=fake_sleep),
            patch("together_sandbox._utils.random.random", return_value=0.0),
        ):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn, RetryConfig(max_attempts=3))

        assert sleep_calls == pytest.approx([0.5, 1.0])

    @pytest.mark.asyncio
    async def test_jitter_is_added_to_base_delay(self):
        """Jitter contributes up to JITTER (0.25s) on top of the base delay."""
        sleep_calls: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleep_calls.append(seconds)

        fn = AsyncMock(return_value=make_error_response(500))

        with (
            patch("together_sandbox._utils.asyncio.sleep", side_effect=fake_sleep),
            patch("together_sandbox._utils.random.random", return_value=1.0),
        ):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn, RetryConfig(max_attempts=3))

        # random = 1.0 → full JITTER (0.25) is applied
        # attempt 1: 0.5 * 1 + 0.25 = 0.75
        # attempt 2: 0.5 * 2 + 0.25 = 1.25
        assert sleep_calls == pytest.approx([0.75, 1.25])


# ─── Async should_retry and on_retry callbacks ─────────────────────────────────


class TestCallApiAsyncCallbacks:
    @pytest.mark.asyncio
    async def test_async_should_retry_returning_false_stops_immediately(self):
        """An async should_retry coroutine is awaited and its False return is honoured."""

        async def should_retry(ctx: RetryContext) -> bool:
            return False

        fn = AsyncMock(return_value=make_error_response(500))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api("testOp", fn, RetryConfig(should_retry=should_retry))

        # should_retry returned False — only one attempt made
        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_should_retry_returning_true_retries(self):
        """An async should_retry coroutine that returns True triggers a retry."""
        data = MagicMock()

        async def should_retry(ctx: RetryContext) -> bool:
            return True

        fn = AsyncMock(
            side_effect=[
                make_error_response(400),  # normally non-retryable
                make_success_response(data),
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _call_api(
                "testOp", fn, RetryConfig(should_retry=should_retry)
            )

        assert result is data
        assert fn.call_count == 2

    @pytest.mark.asyncio
    async def test_async_on_retry_is_awaited_and_called(self):
        """An async on_retry coroutine is awaited once per retry."""
        calls: list[RetryContext] = []

        async def on_retry(ctx: RetryContext) -> None:
            calls.append(ctx)

        fn = AsyncMock(return_value=make_error_response(500))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _call_api(
                    "testOp", fn, RetryConfig(on_retry=on_retry, max_attempts=3)
                )

        # max_attempts=3 → 2 retries → on_retry called twice
        assert len(calls) == 2
        assert calls[0].attempt == 1
        assert calls[1].attempt == 2

    @pytest.mark.asyncio
    async def test_async_on_retry_receives_custom_delay_from_async_should_retry(self):
        """Numeric return from an async should_retry is passed to async on_retry."""
        received_delays: list[float] = []

        async def should_retry(ctx: RetryContext) -> float:
            return 3.0

        async def on_retry(ctx: RetryContext) -> None:
            received_delays.append(ctx.delay)

        data = MagicMock()
        fn = AsyncMock(
            side_effect=[
                make_error_response(500),
                make_success_response(data),
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            await _call_api(
                "testOp",
                fn,
                RetryConfig(should_retry=should_retry, on_retry=on_retry),
            )

        assert received_delays == [3.0]


# ─── 204 / no-body path ────────────────────────────────────────────────────────────


class TestCallApiNoBodyPath:
    @pytest.mark.asyncio
    async def test_returns_none_for_204_no_content(self):
        """parsed=None with a 2xx status is a documented success (e.g. 204 No Content)."""
        fn = AsyncMock(return_value=make_response(204, None))

        result = await _call_api("deleteFile", fn)

        assert result is None
        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_for_200_with_no_body(self):
        """A 200 response with parsed=None is also treated as a success."""
        fn = AsyncMock(return_value=make_response(200, None))

        result = await _call_api("deleteFile", fn)

        assert result is None
        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_call_on_retry_for_no_body_success(self):
        on_retry = MagicMock()
        fn = AsyncMock(return_value=make_response(204, None))

        await _call_api("deleteFile", fn, RetryConfig(on_retry=on_retry))

        on_retry.assert_not_called()

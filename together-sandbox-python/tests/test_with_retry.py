"""Unit tests for the generic ``_with_retry`` primitive.

Mirrors the TS ``describe("withRetry", ...)`` block in
``together-sandbox-typescript/src/utils.test.ts``. HTTP-specific behavior is
covered by ``test_call_api.py``.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from together_sandbox._utils import _with_retry, RetryConfig, RetryContext
from together_sandbox.errors import HttpError

# ─── Success path ─────────────────────────────────────────────────────────────


class TestWithRetrySuccess:
    @pytest.mark.asyncio
    async def test_returns_fn_value_on_first_attempt(self):
        fn = AsyncMock(return_value="ok")

        result = await _with_retry("op", fn)

        assert result == "ok"
        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_call_on_retry_on_success(self):
        on_retry = MagicMock()
        fn = AsyncMock(return_value=42)

        with patch("together_sandbox._utils.asyncio.sleep"):
            await _with_retry("op", fn, RetryConfig(on_retry=on_retry))

        on_retry.assert_not_called()


# ─── Retry behavior ───────────────────────────────────────────────────────────


class TestWithRetryBehavior:
    @pytest.mark.asyncio
    async def test_retries_on_thrown_exception_and_returns_on_success(self):
        fn = AsyncMock(side_effect=[RuntimeError("transient"), "ok"])

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _with_retry("op", fn)

        assert result == "ok"
        assert fn.call_count == 2

    @pytest.mark.asyncio
    async def test_exhausts_max_attempts_then_raises_last_error(self):
        last_err = RuntimeError("final failure")
        fn = AsyncMock(
            side_effect=[
                RuntimeError("first"),
                RuntimeError("second"),
                last_err,
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError) as exc_info:
                await _with_retry("op", fn)

        assert exc_info.value is last_err
        assert fn.call_count == 3

    @pytest.mark.asyncio
    async def test_max_attempts_1_makes_no_retries(self):
        err = RuntimeError("nope")
        fn = AsyncMock(side_effect=err)

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError) as exc_info:
                await _with_retry("op", fn, RetryConfig(max_attempts=1))

        assert exc_info.value is err
        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_retry_called_once_per_failed_attempt_not_on_final(self):
        on_retry = MagicMock()
        fn = AsyncMock(side_effect=RuntimeError("boom"))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _with_retry(
                    "op", fn, RetryConfig(on_retry=on_retry, max_attempts=3)
                )

        # max_attempts=3 → 2 retries → on_retry called twice (not on the
        # final failure that gets re-raised).
        assert on_retry.call_count == 2

    @pytest.mark.asyncio
    async def test_default_is_retryable_retries_any_exception(self):
        """The docker-push case: no custom is_retryable, any exception retries."""
        fn = AsyncMock(
            side_effect=[
                Exception("docker push: connection reset"),
                None,
            ]
        )

        with patch("together_sandbox._utils.asyncio.sleep"):
            await _with_retry("snapshots.pushDockerImage", fn)

        assert fn.call_count == 2


# ─── is_retryable option ──────────────────────────────────────────────────────


class TestWithRetryIsRetryable:
    @pytest.mark.asyncio
    async def test_stops_when_is_retryable_returns_false(self):
        err = RuntimeError("fatal")
        fn = AsyncMock(side_effect=err)
        is_retryable = MagicMock(return_value=False)

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError) as exc_info:
                await _with_retry("op", fn, is_retryable=is_retryable)

        assert exc_info.value is err
        fn.assert_called_once()
        is_retryable.assert_called_once_with(err)

    @pytest.mark.asyncio
    async def test_retries_when_is_retryable_returns_true(self):
        fn = AsyncMock(side_effect=[RuntimeError("transient"), "ok"])

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _with_retry("op", fn, is_retryable=lambda _: True)

        assert result == "ok"
        assert fn.call_count == 2

    @pytest.mark.asyncio
    async def test_is_ignored_when_should_retry_is_set(self):
        """``should_retry`` wins — ``is_retryable`` is the fallback, not an override."""
        is_retryable = MagicMock(return_value=False)
        should_retry = MagicMock(return_value=True)
        fn = AsyncMock(side_effect=[RuntimeError("boom"), "ok"])

        with patch("together_sandbox._utils.asyncio.sleep"):
            result = await _with_retry(
                "op",
                fn,
                RetryConfig(should_retry=should_retry),
                is_retryable=is_retryable,
            )

        assert result == "ok"
        should_retry.assert_called_once()
        is_retryable.assert_not_called()


# ─── should_retry override ────────────────────────────────────────────────────


class TestWithRetryShouldRetry:
    @pytest.mark.asyncio
    async def test_returning_false_short_circuits(self):
        should_retry = MagicMock(return_value=False)
        err = RuntimeError("boom")
        fn = AsyncMock(side_effect=err)

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError) as exc_info:
                await _with_retry(
                    "op",
                    fn,
                    RetryConfig(should_retry=should_retry, max_attempts=5),
                )

        assert exc_info.value is err
        fn.assert_called_once()
        should_retry.assert_called_once()

    @pytest.mark.asyncio
    async def test_returning_float_uses_it_as_custom_delay(self):
        should_retry = MagicMock(return_value=2.5)
        on_retry = MagicMock()
        fn = AsyncMock(side_effect=[RuntimeError("transient"), "ok"])

        with patch("together_sandbox._utils.asyncio.sleep"):
            await _with_retry(
                "op",
                fn,
                RetryConfig(should_retry=should_retry, on_retry=on_retry),
            )

        ctx: RetryContext = on_retry.call_args[0][0]
        assert ctx.delay == 2.5

    @pytest.mark.asyncio
    async def test_returning_true_uses_default_exponential_backoff(self):
        """``True`` keeps the default backoff math (BASE_DELAY * 2^(attempt-1))."""
        should_retry = MagicMock(return_value=True)
        on_retry = MagicMock()
        sleep_calls: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleep_calls.append(seconds)

        fn = AsyncMock(side_effect=RuntimeError("boom"))

        with (
            patch("together_sandbox._utils.asyncio.sleep", side_effect=fake_sleep),
            patch("together_sandbox._utils.random.random", return_value=0.0),
        ):
            with pytest.raises(RuntimeError):
                await _with_retry(
                    "op",
                    fn,
                    RetryConfig(
                        should_retry=should_retry,
                        on_retry=on_retry,
                        max_attempts=3,
                    ),
                )

        # BASE_DELAY = 0.5, JITTER = 0.25, random = 0.0
        # attempt 1 → 0.5 * 2^0 + 0 = 0.5
        # attempt 2 → 0.5 * 2^1 + 0 = 1.0
        assert sleep_calls == pytest.approx([0.5, 1.0])

    @pytest.mark.asyncio
    async def test_retry_context_status_is_none_for_non_http_exception(self):
        should_retry = MagicMock(return_value=False)
        fn = AsyncMock(side_effect=RuntimeError("plain"))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(RuntimeError):
                await _with_retry("myOp", fn, RetryConfig(should_retry=should_retry))

        ctx: RetryContext = should_retry.call_args[0][0]
        assert ctx.operation == "myOp"
        assert ctx.attempt == 1
        assert ctx.status is None
        assert isinstance(ctx.error, Exception)
        assert isinstance(ctx.delay, float)

    @pytest.mark.asyncio
    async def test_retry_context_status_populated_when_exception_has_status(self):
        """``HttpError`` carries ``.status`` — ``_with_retry`` surfaces it in the ctx."""
        should_retry = MagicMock(return_value=False)
        fn = AsyncMock(side_effect=HttpError("server error", 503))

        with patch("together_sandbox._utils.asyncio.sleep"):
            with pytest.raises(HttpError):
                await _with_retry("myOp", fn, RetryConfig(should_retry=should_retry))

        ctx: RetryContext = should_retry.call_args[0][0]
        assert ctx.status == 503
        assert isinstance(ctx.error, HttpError)

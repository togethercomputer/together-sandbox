from __future__ import annotations

import asyncio
import base64
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

import httpx

from .api.models import Error as ApiError
from .api.types import Response
from .sandbox.models.error import Error as SandboxError
from .api.models.sandbox import Sandbox as SandboxModel

# ─── ANSI / encoding helpers ─────────────────────────────────────────────────

_CSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def _strip_ansi(s: str) -> str:
    return _CSI_RE.sub("", s)


def _base32_encode(s: str) -> str:
    return base64.b32encode(s.encode()).decode().lower().rstrip("=")


# ─── Retry types ─────────────────────────────────────────────────────────────

RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({408, 429, 500, 502, 503, 504})

# Connection-level errors that are always retryable by default
_NETWORK_ERRORS = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
)


@dataclass
class RetryContext:
    """Context passed to ``should_retry`` / ``on_retry`` callbacks."""

    operation: str
    """The operation name, e.g. ``'startSandbox'``."""

    attempt: int
    """1-based number of the attempt that just failed."""

    error: Exception
    """The exception that was raised or the parsed error model."""

    status: int | None
    """HTTP status code, or ``None`` for network-level errors."""

    delay: float
    """Seconds until the next attempt (default exponential backoff)."""


@dataclass
class RetryConfig:
    """SDK-level retry configuration.

    Pass to :class:`~together_sandbox.TogetherSandbox` as ``retry=RetryConfig(...)``.

    Example::

        from together_sandbox import TogetherSandbox
        from together_sandbox._utils import RetryConfig, RetryContext

        sdk = TogetherSandbox(
            api_key="...",
            retry=RetryConfig(
                max_attempts=4,
                should_retry=lambda ctx: ctx.operation != "snapshots.create",
                on_retry=lambda ctx: print(f"Retrying {ctx.operation} (attempt {ctx.attempt})"),
            ),
        )
    return result
    """

    max_attempts: int = 3
    """Maximum number of total attempts (including the first). Default: ``3``."""

    should_retry: (
        Callable[[RetryContext], bool | float]
        | Callable[[RetryContext], Awaitable[bool | float]]
        | None
    ) = field(default=None)
    """Override the default retry decision.

    Return ``False`` to stop immediately, ``True`` to retry with the default
    exponential-backoff delay, or a ``float`` (seconds) to retry with a
    custom delay. May be a coroutine function.
    """

    on_retry: (
        Callable[[RetryContext], None]
        | Callable[[RetryContext], Awaitable[None]]
        | None
    ) = field(default=None)
    """Called after each failed attempt, before the next retry.

    Use for logging, metrics, or UI updates. May be a coroutine function.
    """


# ─── _call_api ────────────────────────────────────────────────────────────────

_BASE_DELAY = 0.5  # seconds
_JITTER = 0.25  # seconds


async def _call_api(
    operation: str,
    fn: Callable[[], Awaitable[Response[Any]]],
    retry_config: RetryConfig | None = None,
    context: str = "",
) -> Any:
    """Call a generated ``asyncio_detailed`` API function with retry logic.

    Replaces ``_unwrap_or_raise`` — handles error-model unwrapping and
    transient-failure retries in one place.

    Args:
        operation: Human-readable name used in error messages and
            :class:`RetryContext` (e.g. ``'startSandbox'``).
        fn: A zero-argument async callable returning a ``Response[T]``.
            Must be the ``asyncio_detailed`` variant of a generated function.
        retry_config: Optional retry configuration. Uses SDK defaults when
            ``None`` (3 attempts, retries on 408/429/500/502/503/504 and
            network errors).
        context: Optional extra context appended to error messages
            (e.g. ``"for sandbox 'abc123'"``).

    Returns:
        ``response.parsed`` — the unwrapped success model.

    Raises:
        RuntimeError: When all attempts fail or the error is not retryable.
    """
    max_attempts = retry_config.max_attempts if retry_config else 3
    should_retry_fn = retry_config.should_retry if retry_config else None
    on_retry_fn = retry_config.on_retry if retry_config else None

    suffix = f" {context}" if context else ""

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        # ── 1. Call fn — only catch network-level errors here ─────────
        response: Response[Any] | None = None
        caught_error: Exception | None = None
        try:
            response = await fn()
        except _NETWORK_ERRORS as exc:
            caught_error = exc

        # ── 2. Determine what failed (if anything) ────────────────────
        failed_error: Exception | None = None
        failed_status: int | None = None

        if caught_error is not None:
            # Network-level failure — no HTTP status available
            failed_error = caught_error
            failed_status = None
        elif isinstance(response.parsed, (ApiError, SandboxError)):
            # Documented API error model returned
            failed_status = response.status_code.value
            failed_error = RuntimeError(
                f"Failed to {operation}{suffix}: "
                f"{response.parsed.message} (code: {response.parsed.code})"
            )
        elif response.parsed is None:
            failed_status = response.status_code.value
            if 200 <= failed_status < 300:
                # 2xx with no body (e.g. 204 No Content) — documented success
                return None
            # Undocumented non-2xx status — no model available
            failed_error = RuntimeError(
                f"{operation} returned no response{suffix} (HTTP {failed_status})"
            )
        else:
            # Success
            return response.parsed

        last_error = failed_error

        # ── 3. Decide whether to retry ────────────────────────────────
        if attempt < max_attempts:
            default_delay = (
                _BASE_DELAY * math.pow(2, attempt - 1) + random.random() * _JITTER
            )
            ctx = RetryContext(
                operation=operation,
                attempt=attempt,
                error=failed_error,
                status=failed_status,
                delay=default_delay,
            )

            if should_retry_fn is not None:
                decision: bool | float = should_retry_fn(ctx)
                if asyncio.iscoroutine(decision):
                    decision = await decision  # type: ignore[assignment]
            else:
                # Default: retry on network errors or retryable HTTP codes
                decision = isinstance(caught_error, _NETWORK_ERRORS) or (
                    failed_status is not None
                    and failed_status in RETRYABLE_STATUS_CODES
                )

            if decision is False:
                break

            # bool subclasses int in Python — check bool first to avoid
            # treating True as the numeric value 1
            if isinstance(decision, bool):
                ctx.delay = default_delay  # True → use default backoff
            else:
                ctx.delay = float(decision)  # numeric → custom delay (seconds)

            if on_retry_fn is not None:
                cb_result = on_retry_fn(ctx)
                if asyncio.iscoroutine(cb_result):
                    await cb_result

            await asyncio.sleep(ctx.delay)

    # ── 4. All attempts exhausted (or broke early) ────────────────────
    assert last_error is not None
    raise last_error


def _resolve_connection(sandbox: SandboxModel) -> tuple[str, str]:
    """
    Extract the agent connection details from the Sandbox model.
    """
    if not sandbox.agent_url or not sandbox.agent_token:
        raise RuntimeError("Sandbox has no agent connection details")
    return sandbox.agent_url, sandbox.agent_token

from __future__ import annotations

import asyncio
import base64
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, TypeVar

import httpx

from .api.models import Error as ApiError
from .api.types import Response
from .errors import HttpError
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


# ─── Retry primitives ─────────────────────────────────────────────────────────

_BASE_DELAY = 0.5  # seconds
_JITTER = 0.25  # seconds

T = TypeVar("T")


async def _with_retry(
    operation: str,
    fn: Callable[[], Awaitable[T]],
    retry_config: RetryConfig | None = None,
    *,
    is_retryable: Callable[[Exception], bool] | None = None,
) -> T:
    """Generic retry loop with exponential backoff + jitter.

    Use this for non-HTTP operations (e.g. wrapping a subprocess call) that
    should honor the same :class:`RetryConfig` exposed to SDK consumers as
    :func:`_call_api`. For HTTP calls, prefer ``_call_api`` which adds
    error-model unwrapping on top of this primitive.

    Args:
        operation: Operation name surfaced in ``RetryContext.operation``.
        fn: Zero-argument async callable to attempt.
        retry_config: Optional retry configuration (max attempts, callbacks).
        is_retryable: Predicate used when ``retry_config.should_retry`` is not
            set. Defaults to retrying on any thrown exception — suitable for
            idempotent operations like ``docker push``.

    Returns:
        The resolved value of ``fn`` on the first successful attempt.

    Raises:
        Exception: The last error encountered when all attempts are exhausted
            or when ``is_retryable`` / ``should_retry`` decide to stop.
    """
    max_attempts = retry_config.max_attempts if retry_config else 3
    should_retry_fn = retry_config.should_retry if retry_config else None
    on_retry_fn = retry_config.on_retry if retry_config else None
    is_retryable_fn = is_retryable or (lambda _: True)

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await fn()
        except Exception as exc:
            last_error = exc

            if attempt >= max_attempts:
                break

            default_delay = (
                _BASE_DELAY * math.pow(2, attempt - 1) + random.random() * _JITTER
            )

            # Surface ``.status`` (when present) so user ``should_retry``
            # callbacks can branch on HTTP status. Network-level errors and
            # non-HTTP exceptions leave it ``None``.
            err_status = getattr(exc, "status", None)
            status = err_status if isinstance(err_status, int) else None

            ctx = RetryContext(
                operation=operation,
                attempt=attempt,
                error=exc,
                status=status,
                delay=default_delay,
            )

            if should_retry_fn is not None:
                decision: bool | float = should_retry_fn(ctx)
                if asyncio.iscoroutine(decision):
                    decision = await decision  # type: ignore[assignment]
            else:
                decision = is_retryable_fn(exc)

            if decision is False:
                break

            # bool subclasses int in Python — check bool first to avoid
            # treating True as the numeric value 1.
            if isinstance(decision, bool):
                ctx.delay = default_delay  # True → use default backoff
            else:
                ctx.delay = float(decision)  # numeric → custom delay (seconds)

            if on_retry_fn is not None:
                cb_result = on_retry_fn(ctx)
                if asyncio.iscoroutine(cb_result):
                    await cb_result

            await asyncio.sleep(ctx.delay)

    assert last_error is not None
    raise last_error


# ─── _call_api ────────────────────────────────────────────────────────────────


async def _call_api(
    operation: str,
    fn: Callable[[], Awaitable[Response[Any]]],
    retry_config: RetryConfig | None = None,
    context: str = "",
) -> Any:
    """Call a generated ``asyncio_detailed`` API function with retry logic.

    Handles error-model unwrapping and delegates the retry loop to
    :func:`_with_retry`.

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
        HttpError: For any failure — HTTP error responses surface as
            ``HttpError`` with the actual status code; transport-level
            failures (``httpx.TimeoutException`` / ``ConnectError`` /
            ``RemoteProtocolError``) surface as ``HttpError`` with
            ``status == 0``. The original transport exception is preserved
            on ``__cause__``.
    """
    suffix = f" {context}" if context else ""

    async def _attempt() -> Any:
        # Wrap transport-level failures (httpx.*) into HttpError(status=0) so
        # all failures surface as a single type. Original exception preserved
        # via ``raise ... from exc`` for debugging.
        try:
            response = await fn()
        except _NETWORK_ERRORS as exc:
            raise HttpError(
                f"{operation}{suffix}: {type(exc).__name__}: {exc}",
                0,
            ) from exc

        if isinstance(response.parsed, (ApiError, SandboxError)):
            # Documented API error model returned
            status = response.status_code.value
            raise HttpError(
                f"Failed to {operation}{suffix}: "
                f"{response.parsed.message} (code: {response.parsed.code})",
                status,
            )

        if response.parsed is None:
            status = response.status_code.value
            if 200 <= status < 300:
                # 2xx with no body (e.g. 204 No Content) — documented success
                return None
            # Undocumented non-2xx status — no model available
            raise HttpError(
                f"{operation} returned no response{suffix} (HTTP {status})",
                status,
            )

        # Success
        return response.parsed

    def _is_retryable(exc: Exception) -> bool:
        # All failures (HTTP and transport) arrive as HttpError after the
        # wrapping above. ``status == 0`` is the sentinel for transport
        # failures; documented retryable HTTP codes use their real status.
        status = getattr(exc, "status", None)
        if not isinstance(status, int):
            return False
        return status == 0 or status in RETRYABLE_STATUS_CODES

    return await _with_retry(
        operation,
        _attempt,
        retry_config,
        is_retryable=_is_retryable,
    )


def _resolve_connection(sandbox: SandboxModel) -> tuple[str, str]:
    """
    Extract the agent connection details from the Sandbox model.
    """
    if not sandbox.agent_url or not sandbox.agent_token:
        raise RuntimeError("Sandbox has no agent connection details")
    return sandbox.agent_url, sandbox.agent_token

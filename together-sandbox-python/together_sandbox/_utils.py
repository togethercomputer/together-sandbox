from __future__ import annotations

import asyncio
import base64
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Literal, TypeVar

import httpx

from .api.models import Error as ApiError
from .api.models.termination_policy import TerminationPolicy
from .api.models.termination_snapshot import TerminationSnapshot
from .api.models.tags import Tags
from .api.types import UNSET, Response, Unset
from .errors import HttpError
from .sandbox.models.error import Error as SandboxError
from .sandbox.types import Unset as SandboxUnset
from .api.models.sandbox import Sandbox as SandboxModel


def build_termination_snapshot(snapshot: dict | None | Unset = UNSET):
    """Build a ``TerminationSnapshot`` request model from a plain dict.

    ``snapshot`` is the flat shape
    ``{"aliases": [...], "ttl": int, "tags": {...}}``. Pass
    ``UNSET`` (the default) to leave it unset, or ``None`` to send an explicit
    null (an ephemeral teardown that takes no snapshot).
    """
    # Both generated clients define their own Unset class, and either can reach
    # here depending on which the caller imported; treat both as "leave unset".
    if isinstance(snapshot, (Unset, SandboxUnset)):
        return UNSET
    if snapshot is None:
        return None
    tags = snapshot.get("tags")
    return TerminationSnapshot(
        aliases=snapshot.get("aliases", UNSET),
        ttl=snapshot.get("ttl", UNSET),
        tags=(Tags.from_dict(tags) if tags is not None else UNSET),
    )


def deep_object_tags(tags: dict[str, str] | None):
    """Build the ``Tags`` query model for a `tags` filter.

    The `tags` query parameter is a deepObject, so `{"env": "prod"}` has to go
    over the wire as ``tags[env]=prod``. The generated client merges the model
    straight into the query string instead of bracketing the keys itself, so
    the brackets are applied here.
    """
    if tags is None:
        return UNSET
    return Tags.from_dict({f"tags[{key}]": value for key, value in tags.items()})


def build_termination_policy(termination_policy: dict | None):
    """Build the ``TerminationPolicy`` request model from a plain dict.

    ``termination_policy`` is the nested shape
    ``{"snapshot": {"aliases": [...], "ttl": int, "tags": {...}}}``,
    or None to leave it unset (ephemeral on create). Used by ``create``.
    """
    if termination_policy is None:
        return UNSET
    return TerminationPolicy(
        snapshot=build_termination_snapshot(termination_policy.get("snapshot", {}))
    )

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

    # Classify the call target from the operation name. The convention is:
    #   - ``sandbox.*`` → in-VM sandbox agent
    #   - ``api.*``     → Together management API (Bartender)
    # This drives the transport-failure hint without needing a per-call argument.
    target: Literal["api", "sandbox"] = (
        "sandbox" if operation.startswith("sandbox.") else "api"
    )

    async def _attempt() -> Any:
        # Wrap transport-level failures (httpx.*) into HttpError(status=0) so
        # all failures surface as a single type. Original exception preserved
        # via ``raise ... from exc`` for debugging.
        try:
            response = await fn()
        except _NETWORK_ERRORS as exc:
            # Distinguish timeout from connect for an actionable hint.
            is_timeout = isinstance(exc, httpx.TimeoutException)
            raise HttpError(
                f"{operation}{suffix}: {type(exc).__name__}: {exc}",
                0,
                body=str(exc),
                hint=_hint_for(0, operation, target, is_timeout=is_timeout),
            ) from exc

        if isinstance(response.parsed, (ApiError, SandboxError)):
            # Documented API error model returned
            status = response.status_code.value
            parsed = response.parsed
            details: list[Any] | None = None
            errors_attr = getattr(parsed, "errors", None)
            if isinstance(errors_attr, list):
                details = errors_attr
            raise HttpError(
                f"Failed to {operation}{suffix}: "
                f"{parsed.message} (code: {parsed.code})",
                status,
                code=str(parsed.code),
                details=details,
                body=parsed,
                hint=_hint_for(status, operation, target),
            )

        if response.parsed is None:
            status = response.status_code.value
            if 200 <= status < 300:
                # 2xx with no body (e.g. 204 No Content) — documented success
                return None
            # Undocumented non-2xx status — no model matched the body. Preserve
            # the raw response content so consumers can inspect what came back
            # via ``body=``, and build a human-readable ``dump`` for the error
            # message. Decode defensively: the server may return non-UTF-8
            # bytes on misconfigured endpoints. Fall back to "<empty body>"
            # so the message is never just a bare "HTTP 500 ".
            raw_body: Any = None
            content = getattr(response, "content", None)
            if content is not None:
                try:
                    raw_body = (
                        content.decode("utf-8", errors="replace")
                        if isinstance(content, (bytes, bytearray))
                        else content
                    )
                except Exception:
                    raw_body = content

            # Attempt to extract a human-readable message before falling back
            # to a raw dump. Some server responses carry a ``message`` (or
            # ``error``) string at the top level but omit a field required by
            # the typed model checks (e.g. missing ``errors[]`` or a
            # non-string ``code``). Surfacing that string keeps the error
            # readable without losing the raw body via ``body=``.
            if isinstance(raw_body, str) and raw_body.strip():
                import json as _json

                try:
                    parsed_body = _json.loads(raw_body)
                    if isinstance(parsed_body, dict):
                        msg = parsed_body.get("message") or parsed_body.get("error")
                        if isinstance(msg, str) and msg:
                            code_val = parsed_body.get("code")
                            code_str = (
                                str(code_val)
                                if isinstance(code_val, (str, int))
                                else None
                            )
                            raise HttpError(
                                f"Failed to {operation}{suffix}: {msg}"
                                + (f" (code: {code_str})" if code_str else ""),
                                status,
                                code=code_str,
                                body=raw_body,
                                hint=_hint_for(status, operation, target),
                            )
                except HttpError:
                    raise
                except Exception:
                    pass

            dump = (
                raw_body.strip()
                if isinstance(raw_body, str) and raw_body.strip()
                else "<empty body>"
            )
            raise HttpError(
                f"Failed to {operation}{suffix}: HTTP {status} {dump}",
                status,
                body=raw_body,
                hint=_hint_for(status, operation, target),
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


# ─── Actionable hint lookup ───────────────────────────────────────────────────


def _hint_for(
    status: int,
    operation: str,
    target: Literal["api", "sandbox"],
    *,
    is_timeout: bool = False,
) -> str | None:
    """Build an actionable recovery hint from the failure context.

    Returns ``None`` when no hint applies — the caller's message stands on
    its own. Auto-appended to the :class:`HttpError` message via the class
    constructor and exposed as ``err.hint`` for programmatic branching.

    The hint differentiates between management-API (``api.*``) and in-VM
    sandbox-agent (``sandbox.*``) targets for transport failures, and gives
    resource-specific suggestions for 404s.

    Mirrors :func:`hintFor` in the TypeScript SDK (``src/utils.ts``).
    """
    # Transport-level failure
    if status == 0:
        if target == "sandbox":
            if is_timeout:
                return (
                    "Sandbox did not respond in time. The VM may be "
                    "unresponsive — call sdk.sandboxes.get(id) to check status."
                )
            return (
                "Could not reach the sandbox agent. The VM may have terminated — "
                "call sdk.sandboxes.get(id) to check status."
            )
        if is_timeout:
            return (
                "Request to the Together management API timed out. The "
                "service may be slow or temporarily unreachable."
            )
        return (
            "Could not reach the Together management API. Check your network "
            "connection or TOGETHER_BASE_URL."
        )

    if status == 401:
        return "Authentication failed. Check your TOGETHER_API_KEY."
    if status == 403:
        return (
            "Authenticated but not authorised for this resource. Verify the "
            "project_id and API key scope."
        )

    if status == 404:
        op_lower = operation.lower()
        if "snapshot" in op_lower:
            return (
                "Snapshot does not exist. List available snapshots with "
                "sdk.snapshots.list()."
            )
        if target == "api" and "sandbox" in op_lower:
            return (
                "Sandbox does not exist. List active sandboxes with "
                "sdk.sandboxes.list()."
            )
        return "Resource not found. Verify the ID or alias and retry."

    if status == 429:
        return (
            "Rate limited. Back off and retry; see the Retry-After header "
            "for guidance."
        )
    if status >= 500:
        return (
            "Together backend error. Retry; if it persists, report the issue "
            "with the full request body."
        )

    return None


def _resolve_connection(sandbox: SandboxModel) -> tuple[str, str]:
    """
    Extract the agent connection details from the Sandbox model.
    """
    agent = sandbox.agent
    if not agent or not agent.url or not agent.token:
        raise RuntimeError("Sandbox has no agent connection details")
    return agent.url, agent.token

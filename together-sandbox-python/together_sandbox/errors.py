"""Public exception classes raised by the Together Sandbox SDK.

This module mirrors ``together-sandbox-typescript/src/errors.ts``. Today it
hosts a single class; future exception types (``ApiError``, ``SandboxError``)
will live here too when/if those are promoted from model classes.
"""

from __future__ import annotations

from typing import Any


class HttpError(RuntimeError):
    """Raised when an HTTP request returns a non-success status that doesn't
    match a documented ApiError / SandboxError model, or when a transport-
    level failure occurs (in which case ``status == 0``).

    Carries the HTTP status code as :attr:`status` for retry-decision logic
    and user-supplied ``should_retry`` callbacks (via ``RetryContext.status``).

    Attributes:
        status: HTTP status code, or ``0`` for transport-level failures.
        code: Server-provided error code, when available (Bartender's
            ``Error.code`` string, or sandbox-API numeric code stringified).
        details: Field-level error entries from Bartender's ``Error.errors[]``.
        body: Raw response body for undocumented shapes — preserved so
            nothing is lost.
        hint: Actionable recovery suggestion. Auto-appended to the error
            message and exposed as :attr:`hint`.

    The original transport exception (for ``status == 0``) is preserved on
    :attr:`__cause__` via ``raise ... from exc`` in :func:`_call_api`.

    Mirrors ``HttpError`` in the TypeScript SDK (``src/errors.ts``).
    """

    def __init__(
        self,
        message: str,
        status: int,
        *,
        code: str | None = None,
        details: list[Any] | None = None,
        body: Any = None,
        hint: str | None = None,
    ) -> None:
        full_message = f"{message}\nHint: {hint}" if hint else message
        super().__init__(full_message)
        self.status = status
        self.code = code
        self.details = details
        self.body = body
        self.hint = hint

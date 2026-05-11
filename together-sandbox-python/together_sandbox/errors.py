"""Public exception classes raised by the Together Sandbox SDK.

This module mirrors ``together-sandbox-typescript/src/errors.ts``. Today it
hosts a single class; future exception types (``ApiError``, ``SandboxError``)
will live here too when/if those are promoted from model classes.
"""

from __future__ import annotations


class HttpError(RuntimeError):
    """Raised when an HTTP request returns a non-success status that doesn't
    match a documented ApiError / SandboxError model.

    Carries the HTTP status code as :attr:`status` for retry-decision logic
    and user-supplied ``should_retry`` callbacks (via ``RetryContext.status``).

    Mirrors ``HttpError`` in the TypeScript SDK (``src/errors.ts``).
    """

    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.status = status

/**
 * Public error classes raised by {@link callApi}.
 *
 * Mirrors `together_sandbox.errors` (Python).
 */

// ─── HttpError ────────────────────────────────────────────────────────────────

/**
 * Thrown by `callApi` when an HTTP request fails with a non-success status.
 *
 * Surfaces the HTTP status code via `status` so retry-decision logic and
 * user-supplied `shouldRetry` callbacks can branch on it via
 * `RetryContext.status`. The error message preserves the API's error code
 * and message when the response payload matched a documented shape.
 *
 * Mirrors `together_sandbox.errors.HttpError` (Python).
 */
export class HttpError extends Error {
  /** HTTP status code of the response. */
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "HttpError";
    this.status = status;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

// ─── Type guards ──────────────────────────────────────────────────────────────

/**
 * Returns true when `e` has the shape of a management API error
 * (`{ code: string; message: string; errors: unknown[] }`).
 *
 * Used by `callApi` to detect management-API error payloads when formatting
 * the {@link HttpError} message.
 */
export function isApiErrorShape(
  e: unknown,
): e is { code: string; message: string; errors: unknown[] } {
  return (
    typeof e === "object" &&
    e !== null &&
    "code" in e &&
    typeof (e as Record<string, unknown>).code === "string" &&
    "message" in e &&
    typeof (e as Record<string, unknown>).message === "string" &&
    "errors" in e &&
    Array.isArray((e as Record<string, unknown>).errors)
  );
}

/**
 * Returns true when `e` has the shape of a sandbox API error
 * (`{ code: number; message: string }`).
 *
 * Used by `callApi` to detect in-VM sandbox error payloads when formatting
 * the {@link HttpError} message.
 */
export function isSandboxErrorShape(
  e: unknown,
): e is { code: number; message: string } {
  return (
    typeof e === "object" &&
    e !== null &&
    "code" in e &&
    typeof (e as Record<string, unknown>).code === "number" &&
    "message" in e &&
    typeof (e as Record<string, unknown>).message === "string"
  );
}

/**
 * Public error classes raised by {@link callApi}.
 *
 * Mirrors `together_sandbox.errors` (Python).
 */

// ─── HttpError ────────────────────────────────────────────────────────────────

/**
 * Optional fields enriching an {@link HttpError}.
 *
 * Populated by `callApi` to give consumers actionable information without
 * needing to parse the message string.
 */
export interface HttpErrorOptions {
  /** Server-provided error code (Bartender's `Error.code` string, or sandbox-API numeric code stringified). */
  code?: string;
  /** Bartender's field-level error array (`Error.errors[]`). */
  details?: unknown[];
  /** Raw response body — preserved for undocumented shapes so nothing is lost. */
  body?: unknown;
  /** Actionable recovery suggestion. Auto-appended to the error message and exposed as `.hint`. */
  hint?: string;
  /** Original transport / parsing exception. Exposed via the native ES2022 `cause`. */
  cause?: unknown;
}

/**
 * Thrown by `callApi` when an HTTP request fails with a non-success status,
 * or when a transport-level failure occurs (in which case `status === 0`).
 *
 * Surfaces the HTTP status code via `status` so retry-decision logic and
 * user-supplied `shouldRetry` callbacks can branch on it via
 * `RetryContext.status`. The error message preserves the API's error code
 * and message when the response payload matched a documented shape, and
 * `hint` is auto-appended when provided to make the default stringification
 * actionable.
 *
 * Mirrors `together_sandbox.errors.HttpError` (Python).
 */
export class HttpError extends Error {
  /** HTTP status code of the response. `0` for transport-level failures. */
  readonly status: number;
  /** Server-provided error code, when available. */
  readonly code?: string;
  /** Field-level error details from Bartender's `Error.errors[]`. */
  readonly details?: unknown[];
  /** Raw response body for undocumented shapes. */
  readonly body?: unknown;
  /** Actionable recovery suggestion. */
  readonly hint?: string;

  constructor(message: string, status: number, opts: HttpErrorOptions = {}) {
    const fullMessage = opts.hint ? `${message}\nHint: ${opts.hint}` : message;
    super(fullMessage);
    this.name = "HttpError";
    this.status = status;
    this.code = opts.code;
    this.details = opts.details;
    this.body = opts.body;
    this.hint = opts.hint;
    // Set `cause` manually for compatibility with `lib: ES2020`. Runtime
    // support is fine on Node 16.9+ and all modern browsers.
    if (opts.cause !== undefined) {
      (this as unknown as { cause: unknown }).cause = opts.cause;
    }
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
export function isSandboxErrorShape(e: unknown): e is { code: number; message: string } {
  return (
    typeof e === "object" &&
    e !== null &&
    "code" in e &&
    typeof (e as Record<string, unknown>).code === "number" &&
    "message" in e &&
    typeof (e as Record<string, unknown>).message === "string"
  );
}

/**
 * Typed error classes thrown by {@link callApi}.
 *
 * These mirror the two error models in the Python SDK:
 * - {@link ApiError}    ↔ `together_sandbox/api/models/error.py`
 * - {@link SandboxError} ↔ `together_sandbox/sandbox/models/error.py`
 */

// ─── ApiError ─────────────────────────────────────────────────────────────────

/**
 * Detail item inside an {@link ApiError}.
 * Matches the inline schema of `_Error.errors[]` in `api-clients/api/types.gen.ts`.
 */
export type ApiErrorDetail = {
  parameter?: string;
  code?: string;
  message?: string;
  details?: Record<string, unknown>;
};

/**
 * Thrown when the management API returns a documented error response
 * (e.g. 400 Bad Request, 401 Unauthorized, 404 Not Found).
 *
 * Mirrors `together_sandbox.api.models.Error`.
 */
export class ApiError extends Error {
  /** API-level error code string (e.g. `"NOT_FOUND"`, `"BAD_REQUEST"`). */
  readonly code: string;
  /** HTTP status code of the response. */
  readonly status: number;
  /** Field-level validation details, when provided by the API. */
  readonly errors: ApiErrorDetail[];

  constructor(
    message: string,
    code: string,
    status: number,
    errors: ApiErrorDetail[],
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.errors = errors;
    // Restore prototype chain for `instanceof` checks across transpilation targets
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

// ─── SandboxError ─────────────────────────────────────────────────────────────

/**
 * Thrown when the in-VM sandbox API returns an error response.
 *
 * Mirrors `together_sandbox.sandbox.models.error.Error`.
 */
export class SandboxError extends Error {
  /** Numeric error code returned by the sandbox agent. */
  readonly code: number;
  /** HTTP status code of the response. */
  readonly status: number;

  constructor(message: string, code: number, status: number) {
    super(message);
    this.name = "SandboxError";
    this.code = code;
    this.status = status;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

// ─── Type guards ──────────────────────────────────────────────────────────────

/**
 * Returns true when `e` has the shape of a management API error
 * (`{ code: string; message: string; errors: unknown[] }`).
 *
 * Used by `callApi` to detect management-API error payloads before wrapping
 * them in an {@link ApiError}.
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
 * Used by `callApi` to detect in-VM sandbox error payloads before wrapping
 * them in a {@link SandboxError}.
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

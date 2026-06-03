import type { RetryConfig, RetryContext } from "./types";
import { HttpError, isApiErrorShape, isSandboxErrorShape } from "./errors.js";

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Retry Configuration ─────────────────────────────────────────────────────

export const RETRYABLE_STATUS_CODES = new Set([408, 429, 500, 502, 503, 504]);

const BASE_DELAY = 500; // ms
const JITTER = 250; // ms

/**
 * Generic retry loop with exponential backoff + jitter.
 *
 * Use this for non-HTTP operations (e.g. wrapping a subprocess call) that
 * should honor the same `RetryConfig` shape exposed to SDK consumers as
 * {@link callApi}. For HTTP calls, prefer `callApi` which adds error-model
 * unwrapping on top of this primitive.
 *
 * @param operation - Operation name surfaced in `RetryContext.operation`.
 * @param fn - The work to attempt; receives the 1-based attempt number.
 * @param config - Optional retry configuration (max attempts, callbacks).
 * @param options - Optional `isRetryable` predicate (defaults to retry on any
 *   thrown error) and `context` string appended to thrown error messages.
 * @returns The resolved value of `fn` on the first successful attempt.
 * @throws The last error encountered when all attempts are exhausted or when
 *   `isRetryable` / `shouldRetry` decide to stop.
 */
export async function withRetry<T>(
  operation: string,
  fn: (attempt: number) => Promise<T>,
  config?: RetryConfig,
  options?: {
    /** Decides retry when no HTTP status is available. Defaults to `() => true`. */
    isRetryable?: (error: unknown) => boolean;
    /** Optional context appended to error messages. */
    context?: string;
  },
): Promise<T> {
  const maxAttempts = config?.maxAttempts ?? 3;
  const shouldRetry = config?.shouldRetry;
  const onRetry = config?.onRetry;
  const isRetryable = options?.isRetryable ?? (() => true);
  const context = options?.context;

  let lastError: unknown;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn(attempt);
    } catch (err) {
      lastError =
        err instanceof Error
          ? err
          : new Error(`${operation}${context ? ` ${context}` : ""}: ${String(err)}`);

      if (attempt >= maxAttempts) break;

      const defaultDelay = BASE_DELAY * Math.pow(2, attempt - 1) + Math.random() * JITTER;

      // Surface `.status` to the RetryContext when the thrown error carries
      // one (e.g. `HttpError`) so user `shouldRetry` callbacks can branch on
      // HTTP status. Plain Errors / TypeErrors leave it undefined.
      const errStatus = (lastError as { status?: unknown })?.status;
      const status = typeof errStatus === "number" ? errStatus : undefined;

      const ctx: RetryContext = {
        operation,
        attempt,
        error: lastError,
        status,
        delay: defaultDelay,
      };

      let decision: boolean | number;
      if (shouldRetry) {
        decision = await shouldRetry(ctx);
      } else {
        decision = isRetryable(lastError);
      }

      if (decision === false) break;

      const delay = typeof decision === "number" ? decision : defaultDelay;

      if (onRetry) {
        await onRetry({ ...ctx, delay });
      }

      await sleep(delay);
    }
  }

  if (lastError instanceof Error) throw lastError;
  throw new Error(`${operation}${context ? ` ${context}` : ""}: ${String(lastError)}`);
}

/**
 * Call an API operation with automatic retry logic.
 *
 * @param operation - Operation name (e.g., 'startSandbox') for error messages
 * @param fn - Function that calls the generated client without throwOnError
 * @param config - Optional retry configuration
 * @param context - Optional context appended to error messages (e.g. `"for sandbox 'abc123'"`)
 * @returns The unwrapped data payload
 * @throws {HttpError} For any failure — HTTP error responses surface as
 *   `HttpError` with the actual status; transport-level failures (network,
 *   DNS, TLS, timeout) surface as `HttpError` with `status: 0`.
 */
export async function callApi<T>(
  operation: string,
  fn: () => Promise<{
    data?: T;
    error?: unknown;
    response: Response;
  }>,
  config?: RetryConfig,
  context?: string,
): Promise<T> {
  const suffix = context ? ` ${context}` : "";

  // Classify the call target from the operation name. The convention is:
  //   - `sandbox.*` → in-VM sandbox agent
  //   - `api.*`     → Together management API (Bartender)
  // This drives the transport-failure hint without needing a per-call argument.
  const target: "api" | "sandbox" = operation.startsWith("sandbox.") ? "sandbox" : "api";

  return withRetry<T>(
    operation,
    async () => {
      // ── 1. Call fn — wrap transport-level failures (fetch TypeError) into
      //      `HttpError` with status 0 so all failures surface as a single type.
      let result: { data?: T; error?: unknown; response: Response };
      try {
        result = await fn();
      } catch (err) {
        const causeMessage = err instanceof Error ? err.message : String(err);
        // Detect timeout vs connect from the fetch error's `cause` (Node/undici).
        // Falls back to "connect" when we can't tell — strictly better than
        // today's hint-less failure.
        const errCause = (err as { cause?: { code?: string } }).cause;
        const isTimeout =
          (err instanceof Error && err.name === "AbortError") ||
          errCause?.code === "ETIMEDOUT" ||
          errCause?.code === "UND_ERR_CONNECT_TIMEOUT";
        throw new HttpError(`${operation}${suffix}: ${causeMessage}`, 0, {
          body: err,
          hint: hintFor(0, operation, target, { isTimeout }),
          cause: err,
        });
      }

      if (result.error !== undefined) {
        const err = result.error;
        const status = result.response.status;
        if (isApiErrorShape(err)) {
          // Append field-level details only when present — keeps the common
          // empty-errors case clean (no trailing `\n[]`).
          const tail = err.errors.length > 0 ? `\n${JSON.stringify(err.errors)}` : "";
          throw new HttpError(
            `Failed to ${operation}${suffix}: ${err.message} (code: ${err.code})${tail}`,
            status,
            {
              code: err.code,
              details: err.errors,
              body: err,
              hint: hintFor(status, operation, target),
            },
          );
        }
        if (isSandboxErrorShape(err)) {
          throw new HttpError(
            `Failed to ${operation}${suffix}: ${err.message} (code: ${err.code})`,
            status,
            {
              code: String(err.code),
              body: err,
              hint: hintFor(status, operation, target),
            },
          );
        }
        // Fallback: preserve the original message but surface `.status` via a
        // typed `HttpError` so `isRetryable` and user `shouldRetry` callbacks
        // can branch on the HTTP status code. Stash the raw body so nothing
        // is lost when the response shape is undocumented.
        const fallbackHint = hintFor(status, operation, target);
        if (err instanceof Error) {
          throw new HttpError(err.message, status, {
            body: err,
            hint: fallbackHint,
            cause: err,
          });
        }
        // Unknown error payload — `String(err)` on a plain object would
        // produce the useless `"[object Object]"`, hiding the actual server
        // response. JSON-serialise the body instead so the real cause is
        // visible in logs. Falls back to `String(err)` for values that
        // cannot be stringified (e.g. cyclic references, BigInt).
        let dump: string;
        try {
          dump = JSON.stringify(err);
        } catch {
          dump = String(err);
        }
        throw new HttpError(`Failed to ${operation}${suffix}: HTTP ${status} ${dump}`, status, {
          body: err,
          hint: fallbackHint,
        });
      }

      return result.data as T;
    },
    config,
    {
      context,
      // HTTP-specific predicate: retry on transport failures (`status: 0`)
      // or on documented retryable status codes (extracted from the thrown
      // `HttpError`'s `.status` field).
      isRetryable: (err) => {
        const status = (err as { status?: unknown })?.status;
        if (typeof status !== "number") return false;
        return status === 0 || RETRYABLE_STATUS_CODES.has(status);
      },
    },
  );
}

// ─── Actionable hint lookup ───────────────────────────────────────────────────

/**
 * Build an actionable recovery hint from the failure context.
 *
 * Returns `undefined` when no hint applies — the caller's message stands on
 * its own. Auto-appended to the {@link HttpError} message via
 * {@link HttpError}'s constructor and exposed as `err.hint` for programmatic
 * branching.
 *
 * The hint differentiates between management-API (`api.*`) and in-VM
 * sandbox-agent (`sandbox.*`) targets for transport failures, and gives
 * resource-specific suggestions for 404s.
 *
 * Mirrors `together_sandbox._utils._hint_for` (Python).
 */
function hintFor(
  status: number,
  operation: string,
  target: "api" | "sandbox",
  opts: { isTimeout?: boolean } = {},
): string | undefined {
  // Transport-level failure
  if (status === 0) {
    if (target === "sandbox") {
      return opts.isTimeout
        ? "Sandbox did not respond in time. The VM may be unresponsive — call sdk.sandboxes.get(id) to check status."
        : "Could not reach the sandbox agent. The VM may have stopped — call sdk.sandboxes.get(id) to check status.";
    }
    return opts.isTimeout
      ? "Request to the Together management API timed out. The service may be slow or temporarily unreachable."
      : "Could not reach the Together management API. Check your network connection or TOGETHER_BASE_URL.";
  }

  if (status === 401) {
    return "Authentication failed. Check your TOGETHER_API_KEY.";
  }
  if (status === 403) {
    return "Authenticated but not authorised for this resource. Verify the project_id and API key scope.";
  }

  if (status === 404) {
    const opLower = operation.toLowerCase();
    if (opLower.includes("snapshot")) {
      return "Snapshot does not exist. List available snapshots with sdk.snapshots.list().";
    }
    if (target === "api" && opLower.includes("sandbox")) {
      return "Sandbox does not exist. List active sandboxes with sdk.sandboxes.list().";
    }
    return "Resource not found. Verify the ID or alias and retry.";
  }

  if (status === 429) {
    return "Rate limited. Back off and retry; see the Retry-After header for guidance.";
  }
  if (status >= 500) {
    return "Together backend error. Retry; if it persists, report the issue with the full request body.";
  }

  return undefined;
}

// ─── Snake to Camel Case ──────────────────────────────────────────────────────

/**
 * Converts snake_case property names to camelCase.
 */
type SnakeToCamelCase<S extends string> = S extends `${infer Head}_${infer Tail}`
  ? `${Head}${Capitalize<SnakeToCamelCase<Tail>>}`
  : S;

/**
 * Converts all top-level property keys from snake_case to camelCase.
 * Shallow transformation — only affects direct keys, not nested objects.
 */
export type CamelCasedProperties<T extends object> = {
  [K in keyof T as SnakeToCamelCase<K & string>]: T[K];
};

/**
 * Runtime mapper that converts snake_case object keys to camelCase.
 */
export function camelCaseKeys<T extends Record<string, unknown>>(obj: T): CamelCasedProperties<T> {
  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => [
      key.replace(/_+([a-z])/g, (match, char, offset: number) =>
        offset === 0 ? match : char.toUpperCase(),
      ),
      value,
    ]),
  ) as CamelCasedProperties<T>;
}

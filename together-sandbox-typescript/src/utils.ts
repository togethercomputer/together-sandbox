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
          : new Error(
              `${operation}${context ? ` ${context}` : ""}: ${String(err)}`,
            );

      if (attempt >= maxAttempts) break;

      const defaultDelay =
        BASE_DELAY * Math.pow(2, attempt - 1) + Math.random() * JITTER;

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
  throw new Error(
    `${operation}${context ? ` ${context}` : ""}: ${String(lastError)}`,
  );
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

  return withRetry<T>(
    operation,
    async () => {
      // ── 1. Call fn — wrap transport-level failures (fetch TypeError) into
      //      `HttpError` with status 0 so all failures surface as a single type.
      let result: { data?: T; error?: unknown; response: Response };
      try {
        result = await fn();
      } catch (err) {
        const cause = err instanceof Error ? err.message : String(err);
        throw new HttpError(`${operation}${suffix}: ${cause}`, 0);
      }

      if (result.error !== undefined) {
        const err = result.error;
        const status = result.response.status;
        if (isApiErrorShape(err)) {
          // Append field-level details only when present — keeps the common
          // empty-errors case clean (no trailing `\n[]`).
          const tail =
            err.errors.length > 0 ? `\n${JSON.stringify(err.errors)}` : "";
          throw new HttpError(
            `Failed to ${operation}${suffix}: ${err.message} (code: ${err.code})${tail}`,
            status,
          );
        }
        if (isSandboxErrorShape(err)) {
          throw new HttpError(
            `Failed to ${operation}${suffix}: ${err.message} (code: ${err.code})`,
            status,
          );
        }
        // Fallback: preserve the original message but surface `.status` via a
        // typed `HttpError` so `isRetryable` and user `shouldRetry` callbacks
        // can branch on the HTTP status code.
        if (err instanceof Error) {
          throw new HttpError(err.message, status);
        }
        throw new HttpError(`${operation}${suffix}: ${String(err)}`, status);
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

// ─── Snake to Camel Case ──────────────────────────────────────────────────────

/**
 * Converts snake_case property names to camelCase.
 */
type SnakeToCamelCase<S extends string> =
  S extends `${infer Head}_${infer Tail}`
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
export function camelCaseKeys<T extends Record<string, unknown>>(
  obj: T,
): CamelCasedProperties<T> {
  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => [
      key.replace(/_+([a-z])/g, (match, char, offset: number) =>
        offset === 0 ? match : char.toUpperCase(),
      ),
      value,
    ]),
  ) as CamelCasedProperties<T>;
}

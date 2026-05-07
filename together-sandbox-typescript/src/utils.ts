import type { RetryConfig, RetryContext } from "./types";
import {
  ApiError,
  SandboxError,
  isApiErrorShape,
  isSandboxErrorShape,
  type ApiErrorDetail,
} from "./errors.js";

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Retry Configuration ─────────────────────────────────────────────────────

export const RETRYABLE_STATUS_CODES = new Set([408, 429, 500, 502, 503, 504]);

/**
 * Call an API operation with automatic retry logic.
 *
 * @param operation - Operation name (e.g., 'startSandbox') for error messages
 * @param fn - Function that calls the generated client without throwOnError
 * @param config - Optional retry configuration
 * @param context - Optional context appended to error messages (e.g. `"for sandbox 'abc123'"`)
 * @returns The unwrapped data payload
 * @throws {ApiError} When the management API returns a documented error response
 * @throws {SandboxError} When the in-VM sandbox API returns an error response
 * @throws {TypeError} When a network-level failure occurs
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
  const maxAttempts = config?.maxAttempts ?? 3;
  const shouldRetry = config?.shouldRetry;
  const onRetry = config?.onRetry;

  const BASE_DELAY = 500; // ms
  const JITTER = 250; // ms

  let lastError: unknown;
  let lastStatus: number | undefined;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    // ── 1. Call fn — catch only network errors ──────────────────────
    let result: { data?: T; error?: unknown; response: Response } | undefined;
    let caughtError: unknown;
    try {
      result = await fn();
    } catch (err) {
      caughtError = err;
    }

    // ── 2. Determine what failed ─────────────────────────────────────
    let failedError: unknown;
    let failedStatus: number | undefined;

    if (caughtError !== undefined) {
      failedError = caughtError;
      failedStatus = undefined;
    } else if (result!.error !== undefined) {
      const err = result!.error;
      const status = result!.response.status;
      const suffix = context ? ` ${context}` : "";
      if (isApiErrorShape(err)) {
        failedError = new ApiError(
          `Failed to ${operation}${suffix}: ${err.message} (code: ${err.code})`,
          err.code,
          status,
          err.errors as ApiErrorDetail[],
        );
      } else if (isSandboxErrorShape(err)) {
        failedError = new SandboxError(
          `Failed to ${operation}${suffix}: ${err.message} (code: ${err.code})`,
          err.code,
          status,
        );
      } else {
        failedError =
          err instanceof Error
            ? err
            : new Error(`${operation}: ${String(err)}`);
      }
      failedStatus = status;
    } else {
      return result!.data as T;
    }

    lastError = failedError;
    lastStatus = failedStatus;

    // ── 3. Decide whether to retry ───────────────────────────────────
    if (attempt < maxAttempts) {
      const defaultDelay =
        BASE_DELAY * Math.pow(2, attempt - 1) + Math.random() * JITTER;

      const ctx: RetryContext = {
        operation,
        attempt,
        error: failedError,
        status: failedStatus,
        delay: defaultDelay,
      };

      let decision: boolean | number;
      if (shouldRetry) {
        decision = await shouldRetry(ctx);
      } else {
        decision =
          failedError instanceof TypeError ||
          (failedStatus !== undefined &&
            RETRYABLE_STATUS_CODES.has(failedStatus));
      }

      if (decision === false) break;

      const delay = typeof decision === "number" ? decision : defaultDelay;

      if (onRetry) {
        await onRetry({ ...ctx, delay });
      }

      await sleep(delay);
    }
  }

  // ── 4. All attempts exhausted (or broke early) ───────────────────
  if (lastError instanceof Error) throw lastError;
  throw new Error(
    lastStatus !== undefined
      ? `${operation}: HTTP ${lastStatus}`
      : `${operation}: ${String(lastError)}`,
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

import type {
  Sandbox as SandboxModel,
  CreateSandboxData,
} from "./api-clients/api/types.gen.js";

/**
 * Configuration for the {@link TogetherSandbox} facade.
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
export interface TogetherSandboxConfig {
  /** Together AI API key. */
  apiKey?: string;
  /** Base URL for the management API. Defaults to `https://api.codesandbox.io`. */
  baseUrl?: string;
  /** Retry configuration */
  retry?: RetryConfig;
}

/**
 * Public camelCase version of the management API Sandbox response type.
 */
export type SandboxInfo = CamelCasedProperties<SandboxModel>;

/**
 * Public camelCase version of the create sandbox request parameters.
 */
type RawCreateSandboxParams = CamelCasedProperties<CreateSandboxData["body"]>;

export type CreateSandboxParams = Omit<
  RawCreateSandboxParams,
  "millicpu" | "memoryBytes" | "diskBytes"
> & {
  /** CPU allocation in millicpu. Must be ≥ 250 and a multiple of 250. Default: 1000 (1 vCPU). */
  millicpu?: number;
  /** Memory allocation in bytes. Default: 2 GiB. */
  memoryBytes?: number;
  /** Disk allocation in bytes. Default: 10 GiB. */
  diskBytes?: number;
};

export interface RetryContext {
  operation: string; // e.g. 'startSandbox'
  attempt: number; // 1-based, the attempt that just failed
  error: unknown;
  status?: number; // HTTP status code, when available
  delay: number; // ms before next retry (default computed)
}

export interface RetryConfig {
  maxAttempts?: number; // default 3
  shouldRetry?: (
    ctx: RetryContext,
  ) => boolean | number | Promise<boolean | number>;
  onRetry?: (ctx: RetryContext) => void | Promise<void>;
}

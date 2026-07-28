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
  /** Base URL for the management API. Defaults to `https://api.bartender.codesandbox.io`. */
  baseUrl?: string;
  /** Retry configuration */
  retry?: RetryConfig;
}

/**
 * Public camelCase version of the management API Sandbox response type.
 */
export type SandboxInfo = CamelCasedProperties<SandboxModel>;

/**
 * The lifecycle status of a sandbox.
 */
export type SandboxStatus = SandboxModel["status"];

/**
 * The termination snapshot policy. Omit `terminationPolicy` entirely for an
 * ephemeral sandbox (no snapshot; deleted on termination).
 */
export interface TerminationPolicyParams {
  /** The snapshot produced when the sandbox terminates. */
  snapshot: TerminationSnapshotParams;
}

/**
 * What a teardown snapshots. Passed directly to `terminate()` (and used as the
 * `snapshot` inside a {@link TerminationPolicyParams} at creation).
 */
export interface TerminationSnapshotParams {
  /** Aliases to apply to the produced snapshot. */
  aliases?: string[];
  /** Seconds after creation before the produced snapshot is automatically deleted. */
  ttl?: number;
  /** Arbitrary key/value labels to attach to the produced snapshot. */
  tags?: Record<string, string>;
}

/**
 * Public camelCase version of the create sandbox request parameters.
 */
type RawCreateSandboxParams = CamelCasedProperties<CreateSandboxData["body"]>;

export type CreateSandboxParams = Omit<
  RawCreateSandboxParams,
  "cpu" | "memoryBytes" | "terminationPolicy"
> & {
  /** CPU allocation in cores. Must be between 0.1 and 16. Default: 1 (1 vCPU). */
  cpu?: number;
  /** Memory allocation in bytes. Must be between 1 GB and 8 GB per CPU. Default: 2 GiB. */
  memoryBytes?: number;
  /** Termination snapshot policy. Omit for an ephemeral sandbox. */
  terminationPolicy?: TerminationPolicyParams;
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

import type {
  Sandbox as SandboxModel,
  CreateSandboxData,
} from "./api-clients/api/types.gen.js";
import type { CamelCasedProperties } from "./utils.js";

/**
 * Configuration for the {@link TogetherSandbox} facade.
 */
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
export type CreateSandboxParams = CamelCasedProperties<
  CreateSandboxData["body"]
>;

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

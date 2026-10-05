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
  /**
   * Whether to include a memory snapshot in addition to the filesystem.
   * `true` snapshots both (a hibernate): a sandbox created from the produced
   * snapshot resumes with its processes intact. `false` (the default)
   * snapshots only the filesystem.
   */
  memory?: boolean;
  /** Aliases to apply to the produced snapshot. */
  aliases?: string[];
  /** Seconds after creation before the produced snapshot is automatically deleted. */
  ttl?: number;
  /** Arbitrary key/value labels to attach to the produced snapshot. */
  tags?: Record<string, string>;
}

/**
 * Who may reach a sandbox, and what it may reach.
 *
 * Rules are unordered: when several match, the most specific one decides, and
 * between equally specific rules the more restrictive one does. A host name is
 * more specific than any address, a longer prefix or suffix more than a shorter
 * one, and only then does the port count. A connection no rule matches is
 * allowed.
 *
 * @example
 * ```ts
 * networkPolicy: {
 *   ingress: [{ from: "*", toPort: 3000, access: "allow_with_token" }],
 *   egress: [
 *     { to: "*", toPort: 443, access: "deny" },
 *     { to: "api.openai.com", toPort: 443, access: "allow" },
 *   ],
 * }
 * ```
 */
export interface NetworkPolicyParams {
  /** Rules for requests reaching the sandbox's URL, matched by client address. */
  ingress?: IngressRuleParams[];
  /**
   * Rules for every TCP connection the sandbox opens. Host rules are matched
   * against TLS SNI or the HTTP `Host` header. A sandbox with any `deny` rule
   * may send no UDP other than DNS.
   */
  egress?: EgressRuleParams[];
}

/** A port (`443`), an inclusive range (`"8000-9000"`), or `"*"`. */
export type PortSpec = number | string;

export interface IngressRuleParams {
  /** `"*"`, an IP, or a CIDR. */
  from: string;
  /** The sandbox port the rule covers. Default: every port. */
  toPort?: PortSpec;
  /**
   * `"allow_with_token"` admits a request only if it presents the API key that
   * created the sandbox in the `X-Sandbox-Token` header.
   */
  access: "allow" | "deny" | "allow_with_token";
}

export interface EgressRuleParams {
  /**
   * `"*"`, an IP, a CIDR, a host name, or `"*.domain"` — which matches names
   * under the domain but not the domain itself.
   */
  to: string;
  /** The destination port the rule covers. Default: every port. */
  toPort?: PortSpec;
  access: "allow" | "deny";
}

/**
 * Public camelCase version of the create sandbox request parameters.
 */
type RawCreateSandboxParams = CamelCasedProperties<CreateSandboxData["body"]>;

export type CreateSandboxParams = Omit<
  RawCreateSandboxParams,
  "cpu" | "memoryBytes" | "terminationPolicy" | "networkPolicy"
> & {
  /** CPU allocation in cores. Must be between 0.1 and 16. Default: 1 (1 vCPU). */
  cpu?: number;
  /** Memory allocation in bytes. Must be between 1 GB and 8 GB per CPU. Default: 2 GiB. */
  memoryBytes?: number;
  /** Termination snapshot policy. Omit for an ephemeral sandbox. */
  terminationPolicy?: TerminationPolicyParams;
  /** Network policy. Omit for no restriction. */
  networkPolicy?: NetworkPolicyParams;
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

// Public, hand-written facade types. These mirror the wire shapes of the
// generated OpenAPI clients but are owned by the SDK, so the generated types
// never appear in the published `.d.ts`. See EXPORTED_TYPES.md at the repo root
// for the policy behind this file.
//
// Management API responses are snake_case on the wire and converted to
// camelCase at the facade boundary via `camelCaseKeys` (see Sandboxes.ts /
// Snapshots.ts). The in-VM sandbox API is already camelCase, so those types
// pass through unchanged.

/**
 * Configuration for the {@link TogetherSandbox} facade.
 */
export interface TogetherSandboxConfig {
  /** Together AI API key. */
  apiKey?: string;
  /** Base URL for the management API. Defaults to `https://api.bartender.codesandbox.io`. */
  baseUrl?: string;
  /** Retry configuration */
  retry?: RetryConfig;
}

// ─── Sandbox lifecycle ─────────────────────────────────────────────────────

/** Lifecycle state of a sandbox VM. */
export type SandboxStatus =
  | "created"
  | "starting"
  | "running"
  | "stopping"
  | "stopped";

/** How a sandbox was last started. */
export type StartType = "resume" | "cold_start";

/** Why a sandbox last stopped. */
export type StopReason =
  | "start_failed"
  | "shutdown"
  | "hibernated"
  | "crashed"
  | "oom_killed"
  | "evicted"
  | "node_lost"
  | "cluster_lost";

/** Recovery state after an unexpected stop. */
export type RecoveryStatus =
  | "pending"
  | "recovered"
  | "canceled"
  | "unrecoverable";

/**
 * Information about a sandbox VM, returned by `sdk.sandboxes.create()` and
 * exposed as `sandbox.vmInfo`.
 */
export interface SandboxInfo {
  /** Short identifier (6–8 characters). */
  id: string;
  projectId: string;
  status: SandboxStatus;
  ephemeral: boolean;
  clusterName: string;
  currentVersionNumber: number;
  nextVersionNumber: number;
  /** CPU allocation in millicpu. */
  millicpu: number;
  gpu: number;
  memoryBytes: number;
  diskBytes: number;
  versionCount: number;
  agentVersion: string;
  agentType: string;
  agentToken: string;
  agentUrl: string;
  createdAt: string;
  startRequestedAt: string | null;
  startType: StartType | null;
  startedAt: string | null;
  stopRequestedAt: string | null;
  requestedStopType: "shutdown" | "hibernate" | null;
  stoppedAt: string | null;
  stopReason: StopReason | null;
  specsUpdatedAt: string | null;
  recoveryStatus: RecoveryStatus | null;
  recoveryStartedAt: string | null;
  recoveryFinishedAt: string | null;
  updatedAt: string;
}

/**
 * Parameters for creating a sandbox (`sdk.sandboxes.create()`).
 */
export interface CreateSandboxParams {
  /** Optional explicit sandbox ID. */
  id?: string;
  /** Snapshot ID to create the sandbox from. */
  snapshotId?: string;
  /** Snapshot alias to create the sandbox from. */
  snapshotAlias?: string;
  /** Mark the sandbox as ephemeral. */
  ephemeral?: boolean;
  /** CPU allocation in millicpu. Must be ≥ 250 and a multiple of 250. Default: 1000 (1 vCPU). */
  millicpu?: number;
  /** Memory allocation in bytes. Default: 2 GiB. */
  memoryBytes?: number;
  /** Disk allocation in bytes. Default: 10 GiB. */
  diskBytes?: number;
}

// ─── File system ───────────────────────────────────────────────────────────

/**
 * Metadata for a file or directory, returned by `files.stat()` and
 * `directories.list()`.
 */
export interface FileInfo {
  /** File or directory name. */
  name: string;
  /** Full path to the file or directory. */
  path: string;
  /** Whether this entry is a directory. */
  isDir: boolean;
  /** File size in bytes. */
  size: number;
  /** Last modification time. */
  modTime: string;
}

/** Type of file system event emitted by `files.watch()`. */
export type WatcherEventType =
  | "ADD"
  | "REMOVE"
  | "CHANGE"
  | "connected"
  | "error";

/** A file system change event from `files.watch()`. */
export interface WatcherEvent {
  /** File paths affected by the event. */
  paths: Array<string>;
  /** Type of file system event. */
  type: WatcherEventType;
  /** Timestamp of when the event occurred. */
  timestamp: string;
}

// ─── Execs ─────────────────────────────────────────────────────────────────

/** Exec lifecycle state (e.g. running, stopped, finished). */
export type ExecStatus = string;

/** Stream channel for exec output. */
export type ExecStreamKind = "stdout" | "stderr";

/**
 * Information about an exec (shell command), returned by `execs.create()`,
 * `execs.get()`, `execs.start()`, and `execs.list()`.
 */
export interface ExecInfo {
  /** Exec unique identifier. */
  id: string;
  /** Command being executed. */
  command: string;
  /** Command line arguments. */
  args: Array<string>;
  /** Exec status (e.g. running, stopped, finished). */
  status: ExecStatus;
  /** Process ID of the exec. */
  pid: number;
  /** Whether the exec is using a pty. */
  pty: boolean;
  /** Exit code of the process (only meaningful once the process has exited). */
  exitCode: number;
  /**
   * User the command runs as, in `"uid[:gid]"` form. Omitted when no explicit
   * credentials are set on the exec.
   */
  user?: string;
}

/** Parameters for creating an exec (`execs.create()`). */
export interface CreateExecParams {
  /** Command to execute in the exec. */
  command: string;
  /** Command line arguments. */
  args: Array<string>;
  /** Whether to automatically start the exec (defaults to true). */
  autostart?: boolean;
  /** Whether to start a pty shell session (defaults to false). */
  pty?: boolean;
  /** Working directory for the command (defaults to the workspace directory). */
  cwd?: string;
  /** Environment variables to set for the command. */
  env?: Record<string, string>;
  /**
   * User to run the command as, in `"user[:group]"` form. Each side may be a
   * numeric ID or a name (resolved server-side). Either side may be omitted.
   */
  user?: string;
}

/** A single exec output event from `execs.streamOutput()`. */
export interface ExecOutputEvent {
  /** Stream channel the output came from. */
  type: ExecStreamKind;
  /** Output data. */
  output: string;
  /** Sequence number of the output message. */
  sequence: number;
  /** Timestamp of when the output was generated. */
  timestamp?: string;
  /** Exit code of the process (only present once the process has exited). */
  exitCode?: number;
}

/** Input sent to a running exec via `execs.sendStdin()`. */
export interface ExecStdinInput {
  /** Whether the payload is stdin data or a terminal resize. */
  type: "stdin" | "resize";
  /** The stdin data or resize payload. */
  input: string;
}

/** Result of running a command to completion via `execs.exec()`. */
export interface ExecResult {
  /** Exit code of the process. */
  exitCode: number;
  /** Concatenated stdout + stderr output in arrival order. */
  output: string;
}

// ─── Ports ─────────────────────────────────────────────────────────────────

/** An open port discovered inside the sandbox, returned by `ports.list()`. */
export interface PortInfo {
  /** Port number. */
  port: number;
  /** IP address the port is bound to. */
  address: string;
}

// ─── Retry ─────────────────────────────────────────────────────────────────

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

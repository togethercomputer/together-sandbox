// Public API surface for `together-sandbox`.
//
// Only hand-written facade types are exported here — the auto-generated
// OpenAPI clients under `src/api-clients/` are an internal implementation
// detail and must never appear in this list or in a public method signature.
// See EXPORTED_TYPES.md at the repo root for the policy.

// Unified facade — recommended entry point
export { TogetherSandbox } from "./TogetherSandbox.js";
export { Sandbox } from "./Sandbox.js";
export { HttpError } from "./errors.js";

// Configuration & retry
export type {
  TogetherSandboxConfig,
  RetryConfig,
  RetryContext,
} from "./types.js";

// Sandbox lifecycle
export type {
  SandboxInfo,
  SandboxStatus,
  StopReason,
  StartType,
  RecoveryStatus,
  CreateSandboxParams,
} from "./types.js";
export type { StartOptions, WatchOptions } from "./Sandbox.js";

// File system
export type { FileInfo, WatcherEvent, WatcherEventType } from "./types.js";

// Execs
export type {
  ExecInfo,
  ExecStatus,
  ExecStreamKind,
  CreateExecParams,
  ExecOutputEvent,
  ExecStdinInput,
  ExecResult,
} from "./types.js";

// Ports
export type { PortInfo } from "./types.js";

// Snapshots
export type {
  Snapshot,
  SnapshotArchitecture,
  CreateSnapshotParams,
  CreateContextSnapshotParams,
  CreateImageSnapshotParams,
  CreateSnapshotResult,
  SnapshotProgress,
} from "./Snapshots.js";

import { describe, it, expect } from "vitest";
import * as pkg from "./index.js";

// Compile-time guard: these facade types must remain part of the public
// surface. If any is removed/renamed, this file fails to type-check.
import type {
  TogetherSandboxConfig,
  RetryConfig,
  RetryContext,
  SandboxInfo,
  SandboxStatus,
  StopReason,
  StartType,
  RecoveryStatus,
  CreateSandboxParams,
  StartOptions,
  WatchOptions,
  FileInfo,
  WatcherEvent,
  WatcherEventType,
  ExecInfo,
  ExecStatus,
  ExecStreamKind,
  CreateExecParams,
  ExecOutputEvent,
  ExecStdinInput,
  ExecResult,
  PortInfo,
  Snapshot,
  SnapshotArchitecture,
  CreateSnapshotParams,
  CreateContextSnapshotParams,
  CreateImageSnapshotParams,
  CreateSnapshotResult,
  SnapshotProgress,
} from "./index.js";

// Reference the type imports so `verbatimModuleSyntax`/lint don't flag them.
type _PublicTypes = [
  TogetherSandboxConfig,
  RetryConfig,
  RetryContext,
  SandboxInfo,
  SandboxStatus,
  StopReason,
  StartType,
  RecoveryStatus,
  CreateSandboxParams,
  StartOptions,
  WatchOptions,
  FileInfo,
  WatcherEvent,
  WatcherEventType,
  ExecInfo,
  ExecStatus,
  ExecStreamKind,
  CreateExecParams,
  ExecOutputEvent,
  ExecStdinInput,
  ExecResult,
  PortInfo,
  Snapshot,
  SnapshotArchitecture,
  CreateSnapshotParams,
  CreateContextSnapshotParams,
  CreateImageSnapshotParams,
  CreateSnapshotResult,
  SnapshotProgress,
];

describe("public export surface", () => {
  it("exports the documented runtime values", () => {
    expect(typeof pkg.TogetherSandbox).toBe("function");
    expect(typeof pkg.Sandbox).toBe("function");
    expect(typeof pkg.HttpError).toBe("function");
  });

  it("does not export the internal generated client factories", () => {
    // These leaked the `@hey-api/client-fetch` runtime types into the public
    // surface; consumers needing raw client access import that package directly.
    for (const name of [
      "createApiClient",
      "createApiConfig",
      "createSandboxClient",
      "createSandboxConfig",
    ]) {
      expect(pkg).not.toHaveProperty(name);
    }
  });
});

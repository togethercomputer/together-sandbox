/**
 * Unified Together Sandbox facade.
 *
 * This module provides {@link TogetherSandbox} — a thin wrapper over the two
 * generated SDK clients that handles the startSandbox → SandboxClient handoff
 * transparently.
 *
 * @example
 * ```typescript
 * import { TogetherSandbox } from "@together-sandbox/sdk";
 *
 * const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY! });
 * const sandbox = await sdk.sandboxes.start("my-sandbox-id");
 *
 * const file = await sandbox.files.read("/package.json");
 * await sandbox.shutdown();
 * ```
 *
 * @module
 */

import {
  createClient as createApiClient,
  createConfig as createApiConfig,
} from "./api-clients/api/client/index.js";

import { getInferredApiKey, getInferredBaseUrl } from "./configuration.js";
import { SandboxesNamespace } from "./Sandboxes.js";
import { SnapshotsNamespace } from "./Snapshots.js";
import type { TogetherSandboxConfig } from "./types.js";

// ─── TogetherSandbox (main facade) ──────────────────────────────────────────

/**
 * The main entry point for the Together Sandbox SDK.
 *
 * Provides a unified interface over both the management API (sandboxes,
 * VMs, templates) and the in-VM Sandbox API (files, execs).
 *
 * @example
 * ```typescript
 * import { TogetherSandbox } from "@together-sandbox/sdk";
 *
 * const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY! });
 * const sandbox = await sdk.sandboxes.start("your-sandbox-id");
 *
 * const file = await sandbox.files.read("/package.json");
 * console.log(file.data);
 *
 * await sandbox.shutdown();
 * ```
 */
export class TogetherSandbox {
  /** Sandbox lifecycle operations (start, hibernate, shutdown). */
  readonly sandboxes: SandboxesNamespace;

  /** Snapshot build and management operations. */
  readonly snapshots: SnapshotsNamespace;

  constructor(config?: TogetherSandboxConfig) {
    const apiKey = config?.apiKey ?? getInferredApiKey();

    if (!apiKey) {
      throw new Error(
        "apiKey must be provided or TOGETHER_API_KEY env var must be set",
      );
    }

    const baseUrl = config?.baseUrl ?? getInferredBaseUrl();
    const apiClient = createApiClient(
      createApiConfig({
        baseUrl: `${baseUrl}/api/v1`,
        headers: { Authorization: `Bearer ${apiKey}` },
      }),
    );

    this.sandboxes = new SandboxesNamespace(apiClient, config?.retry);
    this.snapshots = new SnapshotsNamespace(apiClient, baseUrl, config?.retry);
  }
}

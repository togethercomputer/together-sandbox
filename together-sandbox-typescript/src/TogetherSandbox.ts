/**
 * Unified Together Sandbox facade.
 *
 * This module provides {@link TogetherSandbox} — a thin wrapper over the two
 * generated SDK clients that handles the vmStart → SandboxClient handoff
 * transparently.
 *
 * @example
 * ```typescript
 * import { TogetherSandbox } from "@together-sandbox/sdk";
 *
 * const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY! });
 * const sandbox = await sdk.sandboxes.start("my-sandbox-id");
 *
 * const file = await sandbox.files.read({ path: { path: "/package.json" } });
 * await sandbox.shutdown();
 * ```
 *
 * @module
 */

import * as api from "./api-clients/api/index.js";
import * as sandboxApi from "./api-clients/sandbox/index.js";
import {
  createClient as createApiClient,
  createConfig as createApiConfig,
  type Client as ApiClient,
} from "./api-clients/api/client/index.js";
import {
  createClient as createSandboxClient,
  createConfig as createSandboxConfig,
  type Client as SandboxApiClient,
} from "./api-clients/sandbox/client/index.js";
import type { VmStartResponseData } from "./api-clients/api/types.gen.js";

// ─── Internal helpers ────────────────────────────────────────────────────────

/**
 * Select the appropriate (url, token) pair from the vmStart response.
 * Prefers Pint when available, falls back to Pitcher (legacy agent).
 */
export function resolveConnectionDetails(vmInfo: VmStartResponseData): {
  url: string;
  token: string;
} {
  if (vmInfo.use_pint && vmInfo.pint_url && vmInfo.pint_token) {
    return { url: vmInfo.pint_url, token: vmInfo.pint_token };
  }
  return { url: vmInfo.pitcher_url, token: vmInfo.pitcher_token };
}

// ─── Sandbox (connected sandbox) ─────────────────────────────────────────────

/**
 * Configuration for the {@link TogetherSandbox} facade.
 */
export interface TogetherSandboxConfig {
  /** Together AI API key. */
  apiKey: string;
  /** Base URL for the management API. Defaults to `https://api.codesandbox.io`. */
  baseUrl?: string;
}

/**
 * Options for starting a VM.
 */
export interface StartOptions {
  /** Additional VM start request body options (tier, wakeup config, etc.). */
  startOptions?: Parameters<typeof api.vmStart>[0]["body"];
}

/**
 * A running VM with a pre-configured sandbox client attached.
 *
 * All sandbox sub-namespaces (`.files`, `.execs`, `.tasks`, etc.) are
 * delegated directly to the underlying sandbox client, so callers never
 * need to think about client instantiation or URL/token wiring.
 *
 * @example
 * ```typescript
 * const sandbox = await sdk.sandboxes.start("my-sandbox-id");
 * const file = await sandbox.files.read({ path: { path: "/src/index.ts" } });
 * await sandbox.execs.create({ body: { command: "ls", args: ["-la"] } });
 * await sandbox.shutdown();
 * ```
 */
export class Sandbox {
  /** Raw VM start response data (id, cluster, workspace_path, etc.). */
  readonly vmInfo: VmStartResponseData;

  /** The underlying sandbox API client (available for low-level access). */
  readonly sandboxClient: SandboxApiClient;

  /** Reference to the management API client, used for lifecycle calls. */
  private readonly _apiClient: ApiClient;

  constructor(
    vmInfo: VmStartResponseData,
    sandboxClient: SandboxApiClient,
    apiClient: ApiClient,
  ) {
    this.vmInfo = vmInfo;
    this.sandboxClient = sandboxClient;
    this._apiClient = apiClient;
  }

  /** The VM/sandbox ID. */
  get id(): string {
    return this.vmInfo.id;
  }

  // ── Sandbox sub-namespace delegation ──────────────────────────────────────

  /** File system operations (read, create, delete, move, stat). */
  get files() {
    const client = this.sandboxClient;
    return {
      read: (opts: Omit<Parameters<typeof sandboxApi.readFile>[0], "client">) =>
        sandboxApi.readFile({ client, ...opts }),
      create: (opts: Omit<Parameters<typeof sandboxApi.createFile>[0], "client">) =>
        sandboxApi.createFile({ client, ...opts }),
      delete: (opts: Omit<Parameters<typeof sandboxApi.deleteFile>[0], "client">) =>
        sandboxApi.deleteFile({ client, ...opts }),
      action: (opts: Omit<Parameters<typeof sandboxApi.performFileAction>[0], "client">) =>
        sandboxApi.performFileAction({ client, ...opts }),
      stat: (opts: Omit<Parameters<typeof sandboxApi.getFileStat>[0], "client">) =>
        sandboxApi.getFileStat({ client, ...opts }),
    };
  }

  /** Directory operations (list, create, delete). */
  get directories() {
    const client = this.sandboxClient;
    return {
      list: (opts: Omit<Parameters<typeof sandboxApi.listDirectory>[0], "client">) =>
        sandboxApi.listDirectory({ client, ...opts }),
      create: (opts: Omit<Parameters<typeof sandboxApi.createDirectory>[0], "client">) =>
        sandboxApi.createDirectory({ client, ...opts }),
      delete: (opts: Omit<Parameters<typeof sandboxApi.deleteDirectory>[0], "client">) =>
        sandboxApi.deleteDirectory({ client, ...opts }),
    };
  }

  /** Shell exec operations (list, create, get, update, delete, output, stdin, stream). */
  get execs() {
    const client = this.sandboxClient;
    return {
      list: (opts?: Omit<NonNullable<Parameters<typeof sandboxApi.listExecs>[0]>, "client">) =>
        sandboxApi.listExecs({ client, ...opts }),
      create: (opts: Omit<Parameters<typeof sandboxApi.createExec>[0], "client">) =>
        sandboxApi.createExec({ client, ...opts }),
      get: (opts: Omit<Parameters<typeof sandboxApi.getExec>[0], "client">) =>
        sandboxApi.getExec({ client, ...opts }),
      update: (opts: Omit<Parameters<typeof sandboxApi.updateExec>[0], "client">) =>
        sandboxApi.updateExec({ client, ...opts }),
      delete: (opts: Omit<Parameters<typeof sandboxApi.deleteExec>[0], "client">) =>
        sandboxApi.deleteExec({ client, ...opts }),
      output: (opts: Omit<Parameters<typeof sandboxApi.getExecOutput>[0], "client">) =>
        sandboxApi.getExecOutput({ client, ...opts }),
      stdin: (opts: Omit<Parameters<typeof sandboxApi.execExecStdin>[0], "client">) =>
        sandboxApi.execExecStdin({ client, ...opts }),
      stream: (opts?: Omit<NonNullable<Parameters<typeof sandboxApi.streamExecsList>[0]>, "client">) =>
        sandboxApi.streamExecsList({ client, ...opts }),
    };
  }

  /** Task operations (list, get, action, setup). */
  get tasks() {
    const client = this.sandboxClient;
    return {
      list: (opts?: Omit<NonNullable<Parameters<typeof sandboxApi.listTasks>[0]>, "client">) =>
        sandboxApi.listTasks({ client, ...opts }),
      get: (opts: Omit<Parameters<typeof sandboxApi.getTask>[0], "client">) =>
        sandboxApi.getTask({ client, ...opts }),
      action: (opts: Omit<Parameters<typeof sandboxApi.executeTaskAction>[0], "client">) =>
        sandboxApi.executeTaskAction({ client, ...opts }),
      setup: (opts?: Omit<NonNullable<Parameters<typeof sandboxApi.listSetupTasks>[0]>, "client">) =>
        sandboxApi.listSetupTasks({ client, ...opts }),
    };
  }

  /** Port operations (list, stream). */
  get ports() {
    const client = this.sandboxClient;
    return {
      list: (opts?: Omit<NonNullable<Parameters<typeof sandboxApi.listPorts>[0]>, "client">) =>
        sandboxApi.listPorts({ client, ...opts }),
      stream: (opts?: Omit<NonNullable<Parameters<typeof sandboxApi.streamPortsList>[0]>, "client">) =>
        sandboxApi.streamPortsList({ client, ...opts }),
    };
  }

  // ── VM lifecycle methods ──────────────────────────────────────────────────

  /** Hibernate (suspend) this VM. */
  async hibernate(): Promise<void> {
    await api.vmHibernate({ client: this._apiClient, path: { id: this.id } });
  }

  /** Shut down this VM. */
  async shutdown(): Promise<void> {
    await api.vmShutdown({ client: this._apiClient, path: { id: this.id } });
  }

  // ── Static factory (convenience method) ────────────────────────────────

  /**
   * Start a sandbox in a single call (static factory).
   *
   * @example
   * ```typescript
   * const sandbox = await Sandbox.start("my-sandbox-id", {
   *   apiKey: process.env.TOGETHER_API_KEY!,
   * });
   * ```
   */
  static async start(
    sandboxId: string,
    config: TogetherSandboxConfig,
    options?: StartOptions,
  ): Promise<Sandbox> {
    const sdk = new TogetherSandbox(config);
    return sdk.sandboxes.start(sandboxId, options);
  }
}

// ─── SandboxesNamespace ──────────────────────────────────────────────────────

/**
 * Sandbox lifecycle operations, accessed as `sdk.sandboxes.*`.
 */
export class SandboxesNamespace {
  constructor(private readonly _apiClient: ApiClient) {}

  /**
   * Start a VM for the given sandbox ID and return a {@link Sandbox}
   * with a fully wired sandbox client.
   *
   * The URL/token handoff (`use_pint` flag) is handled automatically.
   */
  async start(
    sandboxId: string,
    options?: StartOptions,
  ): Promise<Sandbox> {
    const result = await api.vmStart({
      client: this._apiClient,
      path: { id: sandboxId },
      body: options?.startOptions,
      throwOnError: true,
    });

    const vmInfo = result.data!.data!;
    const { url, token } = resolveConnectionDetails(vmInfo);

    const sandboxClient = createSandboxClient(
      createSandboxConfig({
        baseUrl: url,
        headers: { Authorization: `Bearer ${token}` },
      }),
    );

    return new Sandbox(vmInfo, sandboxClient, this._apiClient);
  }

  /**
   * Fork an existing sandbox and immediately start its VM.
   * Returns a {@link Sandbox} ready to use.
   */
  async fork(
    sandboxId: string,
    forkBody?: Parameters<typeof api.sandboxFork>[0]["body"],
    startOptions?: StartOptions,
  ): Promise<Sandbox> {
    const forkResult = await api.sandboxFork({
      client: this._apiClient,
      path: { id: sandboxId },
      body: forkBody,
      throwOnError: true,
    });

    const newId = forkResult.data!.data!.id;
    return this.start(newId, startOptions);
  }
}

// ─── TogetherSandbox (main facade) ──────────────────────────────────────────

/**
 * The main entry point for the Together Sandbox SDK.
 *
 * Provides a unified interface over both the management API (sandboxes,
 * VMs, templates) and the in-VM Sandbox API (files, execs, tasks).
 *
 * @example
 * ```typescript
 * import { TogetherSandbox } from "@together-sandbox/sdk";
 *
 * const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY! });
 * const sandbox = await sdk.sandboxes.start("your-sandbox-id");
 *
 * const file = await sandbox.files.read({ path: { path: "/package.json" } });
 * console.log(file.data);
 *
 * await sandbox.shutdown();
 * ```
 */
export class TogetherSandbox {
  /** The underlying management API client (exposed for advanced use). */
  readonly apiClient: ApiClient;

  /** Sandbox lifecycle operations (start, fork). */
  readonly sandboxes: SandboxesNamespace;

  constructor(config: TogetherSandboxConfig) {
    this.apiClient = createApiClient(
      createApiConfig({
        baseUrl: config.baseUrl ?? "https://api.codesandbox.io",
        headers: { Authorization: `Bearer ${config.apiKey}` },
      }),
    );
    this.sandboxes = new SandboxesNamespace(this.apiClient);
  }
}

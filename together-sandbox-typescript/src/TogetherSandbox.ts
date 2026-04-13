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
 * const file = await sandbox.files.read("/package.json");
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
import type {
  PreviewTokenCreateRequest,
  PreviewTokenUpdateRequest,
} from "./api-clients/api/types.gen.js";
import type { TaskActionType } from "./api-clients/sandbox/types.gen.js";

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

/**
 * Extract data from an API response, throwing an error if data is missing.
 */
function resolveApiData<T>(response: { data?: T; errors?: (string | { [key: string]: unknown })[] }): T {
  if (!response.data) {
    const errorMessage = response.errors
      ?.map(err => typeof err === "string" ? err : JSON.stringify(err))
      .join(", ") || "Unknown error";
    throw new Error(errorMessage);
  }
  return response.data;
}

// ─── Configuration ───────────────────────────────────────────────────────────

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
 * Options for forking a sandbox.
 */
export type ForkOptions = Parameters<typeof api.sandboxFork>[0]["body"];

/**
 * Options for watching a directory.
 */
export interface WatchOptions {
  /** Whether to watch directories recursively. */
  recursive?: boolean;
  /** Glob patterns to ignore certain files or directories. */
  ignorePatterns?: Array<string>;
}

// ─── Sandbox (connected sandbox) ─────────────────────────────────────────────

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
 * const file = await sandbox.files.read("/src/index.ts");
 * await sandbox.execs.create({ command: "ls", args: ["-la"] });
 * await sandbox.shutdown();
 * ```
 */
export class Sandbox {
  /** Raw VM start response data (id, cluster, workspace_path, etc.). */
  readonly vmInfo: VmStartResponseData;

  /** The underlying sandbox API client (internal). */
  private readonly _sandboxClient: SandboxApiClient;

  /** Reference to the management API client, used for lifecycle calls. */
  private readonly _apiClient: ApiClient;

  constructor(
    vmInfo: VmStartResponseData,
    sandboxClient: SandboxApiClient,
    apiClient: ApiClient,
  ) {
    this.vmInfo = vmInfo;
    this._sandboxClient = sandboxClient;
    this._apiClient = apiClient;
  }

  /** The VM/sandbox ID. */
  get id(): string {
    return this.vmInfo.id;
  }

  // ── Sandbox sub-namespace delegation ──────────────────────────────────────

  /** File system operations (read, create, delete, move, copy, stat, watch). */
  get files() {
    const client = this._sandboxClient;
    return {
      read: async (path: string) => {
        const result = await sandboxApi.readFile({ client, path: { path }, throwOnError: true });
        return result.data.content
      },
      create: async (path: string, content: string | Blob | File) => {
        const body =
          typeof content === "string"
            ? new Blob([content], { type: "application/octet-stream" })
            : content;

        const result = await sandboxApi.createFile({
          client,
          path: { path },
          body,
          throwOnError: true,
        });
        return result.data.content
      },
      delete: async (path: string) => {
        await sandboxApi.deleteFile({ client, path: { path }, throwOnError: true });
      },
      move: async (from: string, to: string) => {
        await sandboxApi.performFileAction({
          client,
          path: { path: from },
          body: { action: "move" as const, destination: to },
          throwOnError: true,
        });
      },
      copy: async (from: string, to: string) => {
        await sandboxApi.performFileAction({
          client,
          path: { path: from },
          body: { action: "copy" as const, destination: to },
          throwOnError: true,
        });
      },
      stat: async (path: string) => {
        const result = await sandboxApi.getFileStat({ client, path: { path }, throwOnError: true });
        return result.data
      },
      watch: async (path: string, options?: WatchOptions) => {
        const result = await sandboxApi.createWatcher({
          client,
          path: { path },
          query: options
            ? {
                recursive: options.recursive,
                ignorePatterns: options.ignorePatterns,
              }
            : undefined,
          throwOnError: true,
        });
        
        return result.stream;
      },
    };
  }

  /** Directory operations (list, create, delete). */
  get directories() {
    const client = this._sandboxClient;
    return {
      list: async (path: string) => {
        const result = await sandboxApi.listDirectory({ client, path: { path }, throwOnError: true });
        return result.data.files
      },
      create: async (path: string) => {
        await sandboxApi.createDirectory({ client, path: { path }, throwOnError: true });
      },
      delete: async (path: string) => {
        await sandboxApi.deleteDirectory({ client, path: { path }, throwOnError: true });
      },
    };
  }

  /** Shell exec operations (list, create, get, update, delete, streamOutput, sendStdin, streamList). */
  get execs() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await sandboxApi.listExecs({ client, throwOnError: true });
        return result.data.execs
      },
      create: async (body: Parameters<typeof sandboxApi.createExec>[0]["body"]) => {
        const result = await sandboxApi.createExec({ client, body, throwOnError: true });
        return result.data
      },
      get: async (id: string) => {
        const result = await sandboxApi.getExec({ client, path: { id }, throwOnError: true });
        return result.data
      },
      update: async (id: string, body: Parameters<typeof sandboxApi.updateExec>[0]["body"]) => {
        const result = await sandboxApi.updateExec({ client, path: { id }, body, throwOnError: true });
        return result.data
      },
      delete: async (id: string) => {
        await sandboxApi.deleteExec({ client, path: { id }, throwOnError: true });
      },
      streamOutput: async (id: string, lastSequence?: number) => {
        const result = await sandboxApi.getExecOutput({
          client,
          path: { id },
          query: lastSequence !== undefined ? { lastSequence } : undefined,
          throwOnError: true,
        });
        return result.data
      },
      sendStdin: async (id: string, body: Parameters<typeof sandboxApi.execExecStdin>[0]["body"]) => {
        const result = await sandboxApi.execExecStdin({ client, path: { id }, body, throwOnError: true });
        return result.data;
      },
      streamList: async () => {
        const result = await sandboxApi.streamExecsList({ client, throwOnError: true });
        return result.stream;
      },
    };
  }

  /** Task operations (list, get, action, setup). */
  get tasks() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await sandboxApi.listTasks({ client, throwOnError: true });
        return result.data.tasks;
      },
      get: async (id: string) => {
        const result = await sandboxApi.getTask({ client, path: { id }, throwOnError: true });
        return result.data.task;
      },
      action: async (id: string, actionType: TaskActionType) => {
        const result = await sandboxApi.executeTaskAction({ client, path: { id }, query: { actionType }, throwOnError: true });
        return result.data;
      },
      setup: async () => {
        const result = await sandboxApi.listSetupTasks({ client, throwOnError: true });
        return result.data.setupTasks;
      },
    };
  }

  /** Port operations (list, streamList). */
  get ports() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await sandboxApi.listPorts({ client, throwOnError: true });
        return result.data.ports;
      },
      streamList: async () => {
        const result = await sandboxApi.streamPortsList({ client, throwOnError: true });
        return result.stream;
      },
    };
  }

  // ── VM lifecycle methods ──────────────────────────────────────────────────

  /** Hibernate (suspend) this VM. */
  async hibernate(): Promise<void> {
    const result = await api.vmHibernate({ client: this._apiClient, path: { id: this.id }, throwOnError: true });
    resolveApiData(result.data);
  }

  /** Shut down this VM. */
  async shutdown(): Promise<void> {
    const result = await api.vmShutdown({ client: this._apiClient, path: { id: this.id }, throwOnError: true });
    resolveApiData(result.data);
  }

  // ── Static factory methods ─────────────────────────────────────────────

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

  /**
   * Hibernate a sandbox by ID without needing a running Sandbox instance.
   *
   * @example
   * ```typescript
   * await Sandbox.hibernate("my-sandbox-id", {
   *   apiKey: process.env.TOGETHER_API_KEY!,
   * });
   * ```
   */
  static async hibernate(
    sandboxId: string,
    config: TogetherSandboxConfig,
  ): Promise<void> {
    const sdk = new TogetherSandbox(config);
    await sdk.sandboxes.hibernate(sandboxId);
  }

  /**
   * Shut down a sandbox by ID without needing a running Sandbox instance.
   *
   * @example
   * ```typescript
   * await Sandbox.shutdown("my-sandbox-id", {
   *   apiKey: process.env.TOGETHER_API_KEY!,
   * });
   * ```
   */
  static async shutdown(
    sandboxId: string,
    config: TogetherSandboxConfig,
  ): Promise<void> {
    const sdk = new TogetherSandbox(config);
    await sdk.sandboxes.shutdown(sandboxId);
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
    const data = resolveApiData(result.data)
    const { url, token } = resolveConnectionDetails(data);

    const sandboxClient = createSandboxClient(
      createSandboxConfig({
        baseUrl: url,
        headers: { Authorization: `Bearer ${token}` },
      }),
    );

    return new Sandbox(data, sandboxClient, this._apiClient);
  }

  /**
   * Fork an existing sandbox and immediately start its VM.
   * Returns a {@link Sandbox} ready to use.
   */
  async fork(
    sandboxId: string,
    forkOptions?: ForkOptions,
  ): Promise<Sandbox> {
    const forkResult = await api.sandboxFork({
      client: this._apiClient,
      path: { id: sandboxId },
      body: forkOptions,
      throwOnError: true,
    });
    const data = resolveApiData(forkResult.data);

    return this.start(data.id);
  }

  /**
   * Hibernate (suspend) a VM by sandbox ID.
   */
  async hibernate(sandboxId: string): Promise<void> {
    const result = await api.vmHibernate({
      client: this._apiClient,
      path: { id: sandboxId },
      throwOnError: true,
    });
    
    resolveApiData(result.data);
  }

  /**
   * Shut down a VM by sandbox ID.
   */
  async shutdown(sandboxId: string): Promise<void> {
    const result = await api.vmShutdown({
      client: this._apiClient,
      path: { id: sandboxId },
      throwOnError: true,
    });
    resolveApiData(result.data);
  }
}

// ─── TokensNamespace ─────────────────────────────────────────────────────────

/**
 * Preview token operations, accessed as `sdk.tokens.*`.
 *
 * Preview tokens allow access to private sandboxes.
 */
export class TokensNamespace {
  constructor(private readonly _apiClient: ApiClient) {}

  /**
   * List all preview tokens for a sandbox.
   */
  async list(sandboxId: string) {
    const result = await api.previewTokenList({
      client: this._apiClient,
      path: { id: sandboxId },
      throwOnError: true,
    });
    const data = resolveApiData(result.data);

    return data.tokens;
  }

  /**
   * Create a new preview token for a sandbox.
   */
  async create(sandboxId: string, body?: PreviewTokenCreateRequest) {
    const result = await api.previewTokenCreate({
      client: this._apiClient,
      path: { id: sandboxId },
      body,
      throwOnError: true,
    });
    const data = resolveApiData(result.data);

    return data.token;
  }

  /**
   * Update an existing preview token.
   */
  async update(sandboxId: string, tokenId: string, body?: PreviewTokenUpdateRequest) {
    const result = await api.previewTokenUpdate({
      client: this._apiClient,
      path: { id: sandboxId, token_id: tokenId },
      body,
      throwOnError: true,
    });
    const data = resolveApiData(result.data);

    return data.token;
  }

  /**
   * Revoke all preview tokens for a sandbox.
   */
  async revokeAll(sandboxId: string) {
    await api.previewTokenRevokeAll({
      client: this._apiClient,
      path: { id: sandboxId },
      throwOnError: true,
    });
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
 * const file = await sandbox.files.read("/package.json");
 * console.log(file.data);
 *
 * await sandbox.shutdown();
 * ```
 */
export class TogetherSandbox {
  /** Sandbox lifecycle operations (start, fork, hibernate, shutdown). */
  readonly sandboxes: SandboxesNamespace;

  /** Preview token operations (list, create, update, revokeAll). */
  readonly tokens: TokensNamespace;

  constructor(config: TogetherSandboxConfig) {
    const apiClient = createApiClient(
      createApiConfig({
        baseUrl: config.baseUrl ?? "https://api.codesandbox.io",
        headers: { Authorization: `Bearer ${config.apiKey}` },
      }),
    );
    this.sandboxes = new SandboxesNamespace(apiClient);
    this.tokens = new TokensNamespace(apiClient);
  }
}

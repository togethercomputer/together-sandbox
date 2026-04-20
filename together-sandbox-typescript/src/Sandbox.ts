import * as api from "./api-clients/api/index.js";
import * as sandboxApi from "./api-clients/sandbox/index.js";
import type { TaskActionType } from "./api-clients/sandbox/types.gen.js";
import { type Client as SandboxApiClient } from "./api-clients/sandbox/client/index.js";
import type { Sandbox as SandboxModel } from "./api-clients/api/types.gen.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import type { TogetherSandboxConfig } from "./configuration.js";
import { TogetherSandbox } from "./TogetherSandbox.js";

/**
 * Options for watching a directory.
 */
export interface WatchOptions {
  /** Whether to watch directories recursively. */
  recursive?: boolean;
  /** Glob patterns to ignore certain files or directories. */
  ignorePatterns?: Array<string>;
}

/**
 * Options for starting a VM.
 */
export interface StartOptions {
  /** Additional sandbox start request body options. */
  startOptions?: Parameters<typeof api.startSandbox>[0]["body"];
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
 * const file = await sandbox.files.read("/src/index.ts");
 * await sandbox.execs.create({ command: "ls", args: ["-la"] });
 * await sandbox.shutdown();
 * ```
 */
export class Sandbox {
  /** Raw VM start response data (id, cluster, workspace_path, etc.). */
  readonly vmInfo: SandboxModel;

  /** The underlying sandbox API client (internal). */
  private readonly _sandboxClient: SandboxApiClient;

  /** Reference to the management API client, used for lifecycle calls. */
  private readonly _apiClient: ApiClient;

  constructor(
    vmInfo: SandboxModel,
    sandboxClient: SandboxApiClient,
    apiClient: ApiClient,
  ) {
    this.vmInfo = vmInfo;
    this._sandboxClient = sandboxClient;
    this._apiClient = apiClient;
  }

  /** The VM/sandbox ID. */
  get id(): string {
    if (!this.vmInfo.id) throw new Error("Sandbox has no ID");
    return this.vmInfo.id;
  }

  // ── Sandbox sub-namespace delegation ──────────────────────────────────────

  /** File system operations (read, create, delete, move, copy, stat, watch). */
  get files() {
    const client = this._sandboxClient;
    return {
      read: async (path: string) => {
        const result = await sandboxApi.readFile({
          client,
          path: { path },
          throwOnError: true,
        });
        return result.data.content;
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
        return result.data.content;
      },
      delete: async (path: string) => {
        await sandboxApi.deleteFile({
          client,
          path: { path },
          throwOnError: true,
        });
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
        const result = await sandboxApi.getFileStat({
          client,
          path: { path },
          throwOnError: true,
        });
        return result.data;
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
        const result = await sandboxApi.listDirectory({
          client,
          path: { path },
          throwOnError: true,
        });
        return result.data.files;
      },
      create: async (path: string) => {
        await sandboxApi.createDirectory({
          client,
          path: { path },
          throwOnError: true,
        });
      },
      delete: async (path: string) => {
        await sandboxApi.deleteDirectory({
          client,
          path: { path },
          throwOnError: true,
        });
      },
    };
  }

  /** Shell exec operations (list, create, get, update, delete, streamOutput, sendStdin, streamList). */
  get execs() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await sandboxApi.listExecs({
          client,
          throwOnError: true,
        });
        return result.data.execs;
      },
      create: async (
        body: Parameters<typeof sandboxApi.createExec>[0]["body"],
      ) => {
        const result = await sandboxApi.createExec({
          client,
          body,
          throwOnError: true,
        });
        return result.data;
      },
      get: async (id: string) => {
        const result = await sandboxApi.getExec({
          client,
          path: { id },
          throwOnError: true,
        });
        return result.data;
      },
      update: async (
        id: string,
        body: Parameters<typeof sandboxApi.updateExec>[0]["body"],
      ) => {
        const result = await sandboxApi.updateExec({
          client,
          path: { id },
          body,
          throwOnError: true,
        });
        return result.data;
      },
      delete: async (id: string) => {
        await sandboxApi.deleteExec({
          client,
          path: { id },
          throwOnError: true,
        });
      },
      streamOutput: async (id: string, lastSequence?: number) => {
        const result = await sandboxApi.streamExecOutput({
          client,
          path: { id },
          query: lastSequence !== undefined ? { lastSequence } : undefined,
          throwOnError: true,
        });
        return result.stream;
      },
      getOutput: async (id: string, lastSequence?: number) => {
        const result = await sandboxApi.getExecOutput({
          client,
          path: { id },
          query: lastSequence !== undefined ? { lastSequence } : undefined,
          throwOnError: true,
        });
        return result.data;
      },
      sendStdin: async (
        id: string,
        body: Parameters<typeof sandboxApi.execExecStdin>[0]["body"],
      ) => {
        const result = await sandboxApi.execExecStdin({
          client,
          path: { id },
          body,
          throwOnError: true,
        });
        return result.data;
      },
      streamList: async () => {
        const result = await sandboxApi.streamExecsList({
          client,
          throwOnError: true,
        });
        return result.stream;
      },
    };
  }

  /** Task operations (list, get, action, setup). */
  get tasks() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await sandboxApi.listTasks({
          client,
          throwOnError: true,
        });
        return result.data.tasks;
      },
      get: async (id: string) => {
        const result = await sandboxApi.getTask({
          client,
          path: { id },
          throwOnError: true,
        });
        return result.data.task;
      },
      action: async (id: string, actionType: TaskActionType) => {
        const result = await sandboxApi.executeTaskAction({
          client,
          path: { id },
          query: { actionType },
          throwOnError: true,
        });
        return result.data;
      },
      listSetup: async () => {
        const result = await sandboxApi.listSetupTasks({
          client,
          throwOnError: true,
        });
        return result.data.setupTasks;
      },
    };
  }

  /** Port operations (list, streamList). */
  get ports() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await sandboxApi.listPorts({
          client,
          throwOnError: true,
        });
        return result.data.ports;
      },
      streamList: async () => {
        const result = await sandboxApi.streamPortsList({
          client,
          throwOnError: true,
        });
        return result.stream;
      },
    };
  }

  // ── VM lifecycle methods ──────────────────────────────────────────────────

  /** Hibernate (suspend) this VM. */
  async hibernate(): Promise<void> {
    await api.stopSandbox({
      client: this._apiClient,
      path: { id: this.id },
      body: { stop_type: "hibernate" },
      throwOnError: true,
    });
  }

  /** Shut down this VM. */
  async shutdown(): Promise<void> {
    await api.stopSandbox({
      client: this._apiClient,
      path: { id: this.id },
      body: { stop_type: "shutdown" },
      throwOnError: true,
    });
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

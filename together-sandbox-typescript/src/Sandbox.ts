import * as api from "./api-clients/api/index.js";
import * as sandboxApi from "./api-clients/sandbox/index.js";
import { type Client as SandboxApiClient } from "./api-clients/sandbox/client/index.js";
import type { RetryConfig, SandboxInfo, TogetherSandboxConfig } from "./types.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { TogetherSandbox } from "./TogetherSandbox.js";
import { callApi } from "./utils.js";
import { describeLifecycleFailure } from "./lifecycle.js";

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
  /** Version number to start. Uses the current version if not provided. */
  versionNumber?: number;
}

/**
 * A running VM with a pre-configured sandbox client attached.
 *
 * All sandbox sub-namespaces (`.files`, `.execs`, etc.) are
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
  constructor(
    public readonly vmInfo: SandboxInfo,
    private readonly _sandboxClient: SandboxApiClient,
    private readonly _apiClient: ApiClient,
    private readonly _retryConfig?: RetryConfig,
  ) {}

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
        const result = await callApi(
          "sandbox.files.read",
          () =>
            sandboxApi.readFile({
              client,
              path: { path },
            }),
          this._retryConfig,
        );
        return result.content;
      },
      create: async (path: string, content: string | Blob | File) => {
        const body =
          typeof content === "string"
            ? new Blob([content], { type: "application/octet-stream" })
            : content;

        const result = await callApi(
          "sandbox.files.create",
          () =>
            sandboxApi.createFile({
              client,
              path: { path },
              body,
            }),
          this._retryConfig,
        );
        return result.content;
      },
      delete: async (path: string) => {
        await callApi(
          "sandbox.files.delete",
          () =>
            sandboxApi.deleteFile({
              client,
              path: { path },
            }),
          this._retryConfig,
        );
      },
      move: async (from: string, to: string) => {
        await callApi(
          "sandbox.files.move",
          () =>
            sandboxApi.performFileAction({
              client,
              path: { path: from },
              body: { action: "move" as const, destination: to },
            }),
          this._retryConfig,
        );
      },
      copy: async (from: string, to: string) => {
        await callApi(
          "sandbox.files.copy",
          () =>
            sandboxApi.performFileAction({
              client,
              path: { path: from },
              body: { action: "copy" as const, destination: to },
            }),
          this._retryConfig,
        );
      },
      stat: async (path: string) => {
        const result = await callApi(
          "sandbox.files.stat",
          () =>
            sandboxApi.getFileStat({
              client,
              path: { path },
            }),
          this._retryConfig,
        );
        return result;
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
        const result = await callApi(
          "sandbox.directories.list",
          () =>
            sandboxApi.listDirectory({
              client,
              path: { path },
            }),
          this._retryConfig,
        );
        return result.files;
      },
      create: async (path: string) => {
        await callApi(
          "sandbox.directories.create",
          () =>
            sandboxApi.createDirectory({
              client,
              path: { path },
            }),
          this._retryConfig,
        );
      },
      delete: async (path: string) => {
        await callApi(
          "sandbox.directories.delete",
          () =>
            sandboxApi.deleteDirectory({
              client,
              path: { path },
            }),
          this._retryConfig,
        );
      },
    };
  }

  /** Shell exec operations (list, create, get, start, delete, streamOutput, sendStdin, streamList). */
  get execs() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await callApi(
          "sandbox.execs.list",
          () =>
            sandboxApi.listExecs({
              client,
            }),
          this._retryConfig,
        );
        return result.execs;
      },
      create: async (body: Parameters<typeof sandboxApi.createExec>[0]["body"]) => {
        const result = await callApi(
          "sandbox.execs.create",
          () =>
            sandboxApi.createExec({
              client,
              body,
            }),
          this._retryConfig,
        );
        return result;
      },
      get: async (id: string) => {
        const result = await callApi(
          "sandbox.execs.get",
          () =>
            sandboxApi.getExec({
              client,
              path: { id },
            }),
          this._retryConfig,
        );
        return result;
      },
      start: async (id: string) => {
        const result = await callApi(
          "sandbox.execs.start",
          () =>
            sandboxApi.startExec({
              client,
              path: { id },
              body: {},
            }),
          this._retryConfig,
        );
        return result;
      },
      delete: async (id: string) => {
        await callApi(
          "sandbox.execs.delete",
          () =>
            sandboxApi.deleteExec({
              client,
              path: { id },
            }),
          this._retryConfig,
        );
      },
      streamOutput: async (id: string, lastSequence?: number) => {
        const result = await sandboxApi.streamExecOutput({
          client,
          path: { id },
          query: lastSequence !== undefined ? { lastSequence } : undefined,
        });
        return result.stream;
      },
      exec: async (
        command: string,
        args: string[],
        opts?: Omit<
          Parameters<typeof sandboxApi.createExec>[0]["body"],
          "command" | "args" | "autostart"
        >,
      ) => {
        const exec = await this.execs.create({
          ...opts,
          command,
          args,
          autostart: true,
        });

        const chunks: string[] = [];
        let exitCode: number | undefined;
        const stream = await this.execs.streamOutput(exec.id);

        for await (const event of stream) {
          chunks.push(event.output);
          if (typeof event.exitCode === "number") {
            exitCode = event.exitCode;
            break;
          }
        }

        if (exitCode === undefined) {
          throw new Error(
            `exec(${command}) stream ended without an exit code — the process may have been killed externally or the sandbox shut down`,
          );
        }

        return { exitCode, output: chunks.join("") };
      },
      getOutput: async (id: string, lastSequence?: number) => {
        const events = await callApi(
          "sandbox.execs.getOutput",
          () =>
            sandboxApi.getExecOutput({
              client,
              path: { id },
              query: lastSequence !== undefined ? { lastSequence } : undefined,
            }),
          this._retryConfig,
        );
        const exitCode = events.find((e) => typeof e.exitCode === "number")?.exitCode;
        const output = events.map((e) => e.output).join("");
        return { exitCode, output };
      },
      sendStdin: async (
        id: string,
        body: Parameters<typeof sandboxApi.execExecStdin>[0]["body"],
      ) => {
        const result = await callApi(
          "sandbox.execs.sendStdin",
          () =>
            sandboxApi.execExecStdin({
              client,
              path: { id },
              body,
            }),
          this._retryConfig,
        );
        return result;
      },
      streamList: async () => {
        const result = await sandboxApi.streamExecsList({
          client,
        });
        return result.stream;
      },
    };
  }

  /** Port operations (list, streamList). */
  get ports() {
    const client = this._sandboxClient;
    return {
      list: async () => {
        const result = await callApi(
          "sandbox.ports.list",
          () =>
            sandboxApi.listPorts({
              client,
            }),
          this._retryConfig,
        );
        return result.ports;
      },
      streamList: async () => {
        const result = await sandboxApi.streamPortsList({
          client,
        });
        return result.stream;
      },
    };
  }

  // ── VM lifecycle methods ──────────────────────────────────────────────────

  /** Hibernate (suspend) this VM. */
  async hibernate(): Promise<void> {
    await callApi(
      "api.stopSandbox",
      () =>
        api.stopSandbox({
          client: this._apiClient,
          path: { id: this.id },
          body: { stop_type: "hibernate" },
        }),
      this._retryConfig,
    );

    const waitResult = await callApi(
      "api.waitForSandbox",
      () =>
        api.waitForSandbox({
          client: this._apiClient,
          path: { id: this.id },
        }),
      this._retryConfig,
    );

    if (waitResult.status !== "stopped") {
      throw new Error(describeLifecycleFailure(waitResult, "stopped"));
    }
  }

  /** Shut down this VM. */
  async shutdown(): Promise<void> {
    await callApi(
      "api.stopSandbox",
      () =>
        api.stopSandbox({
          client: this._apiClient,
          path: { id: this.id },
          body: { stop_type: "shutdown" },
        }),
      this._retryConfig,
    );
    const waitResult = await callApi(
      "api.waitForSandbox",
      () =>
        api.waitForSandbox({
          client: this._apiClient,
          path: { id: this.id },
        }),
      this._retryConfig,
    );

    if (waitResult.status !== "stopped") {
      throw new Error(describeLifecycleFailure(waitResult, "stopped"));
    }
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
  static async hibernate(sandboxId: string, config: TogetherSandboxConfig): Promise<void> {
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
  static async shutdown(sandboxId: string, config: TogetherSandboxConfig): Promise<void> {
    const sdk = new TogetherSandbox(config);
    await sdk.sandboxes.shutdown(sandboxId);
  }
}

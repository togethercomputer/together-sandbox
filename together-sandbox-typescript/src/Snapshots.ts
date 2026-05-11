import * as api from "./api-clients/api/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { isLocalEnvironment } from "./configuration.js";
import { callApi, sleep, withRetry } from "./utils.js";
import {
  buildDockerImage,
  dockerLogin,
  isDockerAvailable,
  pushDockerImage,
} from "./docker.js";
import { randomUUID } from "crypto";
import type { RetryConfig } from "./types.js";

export type SnapshotProgress = { output: string } & (
  | { step: "prepare" }
  | { step: "build" }
  | { step: "auth" }
  | { step: "push" }
  | { step: "register" }
  | { step: "memory-snapshot" }
  | { step: "alias" }
);

export type Snapshot = api.Snapshot;

/**
 * Parameters for creating a snapshot
 */
export type CreateContextSnapshotParams = {
  context: string;
  dockerfile?: string;
  alias?: string;
  onProgress?: (event: SnapshotProgress) => void;
  /** @internal */
  memorySnapshot?: boolean;
};

export type CreateImageSnapshotParams = {
  image: string;
  alias?: string;
  onProgress?: (event: SnapshotProgress) => void;
};
export type CreateSnapshotParams =
  | CreateContextSnapshotParams
  | CreateImageSnapshotParams;

/**
 * Result of a successful snapshot creation.
 */
export interface CreateSnapshotResult {
  /** ID of the created (or memory-snapshotted) snapshot. */
  snapshotId: string;
  /** The alias that was applied, if any. */
  alias?: string;
}

function stripAnsiCodes(str: string) {
  // Matches ESC [ params … finalChar
  //   \x1B       = ESC
  //   \[         = literal "["
  //   [0-?]*     = any parameter bytes (digits, ;, ?)
  //   [ -/]*     = any intermediate bytes (space through /)
  //   [@-~]      = final byte ( @ A–Z [ \ ] ^ _ ` a–z { | } ~ )
  const CSI_REGEX = /\x1B\[[0-?]*[ -/]*[@-~]/g;
  return str.replace(CSI_REGEX, "");
}

export type ImageReference = {
  registry?: string;
  repository?: string;
  name: string;
  tag?: string;
};

/**
 * Snapshot build and management operations, accessed as `sdk.snapshots.*`.
 */
export class SnapshotsNamespace {
  constructor(
    private readonly _apiClient: ApiClient,
    private readonly _baseUrl: string,
    private readonly _retryConfig?: RetryConfig,
  ) {}

  // ─── Public entry points ──────────────────────────────────────────────────

  async getById(id: string): Promise<Snapshot> {
    const result = await callApi(
      "snapshots.getById",
      () =>
        api.getSnapshot({
          client: this._apiClient,
          path: { id },
        }),
      this._retryConfig,
    );

    return result;
  }

  async getByAlias(alias: string): Promise<Snapshot> {
    const result = await callApi(
      "snapshots.getByAlias",
      () =>
        api.getSnapshotByAlias({
          client: this._apiClient,
          path: { alias },
        }),
      this._retryConfig,
    );

    return result;
  }

  async list(): Promise<Snapshot[]> {
    const result = await callApi(
      "snapshots.list",
      () =>
        api.listSnapshots({
          client: this._apiClient,
        }),
      this._retryConfig,
    );

    return result;
  }

  async alias(snapshotId: string, alias: string): Promise<void> {
    await callApi(
      "snapshots.alias",
      () =>
        api.aliasSnapshot({
          client: this._apiClient,
          path: { snapshot_id: snapshotId },
          body: { alias },
        }),
      this._retryConfig,
    );
  }

  async deleteById(id: string): Promise<void> {
    await callApi(
      "snapshots.deleteById",
      () =>
        api.deleteSnapshot({
          client: this._apiClient,
          path: { id },
        }),
      this._retryConfig,
    );
  }

  async deleteByAlias(alias: string): Promise<void> {
    // Ensure consistency with API
    const cleanAlias = alias.startsWith("@") ? alias.slice(1) : alias;

    await callApi(
      "snapshots.deleteByAlias",
      () =>
        api.deleteSnapshotByAlias({
          client: this._apiClient,
          path: { alias: cleanAlias },
        }),
      this._retryConfig,
    );
  }

  /**
   * Create a snapshot from a Docker build context or a public Docker image.
   *
   * Pass `{ context, dockerfile?, alias?, onProgress?, memorySnapshot? }` to build from a Dockerfile.
   * Pass `{ image, alias?, onProgress? }` to register a public Docker image.
   *
   * @note The `snapshots.create` operation is not idempotent: retrying on a 500 error
   * after the snapshot has been created will register a duplicate. If you are using
   * retry configuration, consider excluding this operation via:
   * `shouldRetry: ({ operation }) => operation !== 'snapshots.create'`
   */
  async create(params: CreateSnapshotParams): Promise<CreateSnapshotResult> {
    if ("context" in params) {
      // Build from context
      const dockerAvailable = await isDockerAvailable();
      if (!dockerAvailable) {
        console.error(
          "Docker is not available. Please install Docker to use beta build mode.",
        );
        process.exit(1);
      }

      return this._buildAndRegister(params);
    } else {
      // Create from image
      params.onProgress?.({
        step: "register",
        output: "Registering snapshot...",
      });

      const snapshotData = await callApi(
        "snapshots.create",
        () =>
          api.createSnapshot({
            client: this._apiClient,
            body: { image: params.image, architecture: "amd64" },
          }),
        this._retryConfig,
      );

      // Create alias if needed
      if (params.alias) {
        const alias = params.alias;

        params.onProgress?.({
          step: "alias",
          output: "Creating alias...",
        });

        await callApi(
          "snapshots.alias",
          () =>
            api.aliasSnapshot({
              client: this._apiClient,
              path: { snapshot_id: snapshotData.id },
              body: { alias },
            }),
          this._retryConfig,
        );
      }

      return {
        snapshotId: snapshotData.id,
        alias: params.alias,
      };
    }
  }

  // ─── Private helpers ──────────────────────────────────────────────────────

  private async _buildAndRegister(
    params: CreateContextSnapshotParams,
  ): Promise<CreateSnapshotResult> {
    const architecture: "amd64" | "arm64" =
      process.arch === "arm64" && isLocalEnvironment(this._baseUrl)
        ? "arm64"
        : "amd64";
    const dockerfilePath = params.dockerfile;
    const context = params.context;
    const apiClient = this._apiClient;

    const credential = await callApi(
      "snapshots.issueContainerRegistryCredential",
      () =>
        api.issueContainerRegistryCredential({
          client: this._apiClient,
        }),
      this._retryConfig,
    );
    const registryUrl = credential.registry_url;
    const registryHost = registryUrl.split("/")[0];
    const imageName = `image-${randomUUID().toLowerCase()}`;
    const tag = randomUUID().toLowerCase();
    const fullImageName = `${registryUrl}/${imageName}:${tag}`;

    // Docker Build
    params.onProgress?.({
      step: "prepare",
      output: "Preparing snapshot...",
    });
    params.onProgress?.({ step: "build", output: "Building snapshot..." });
    await buildDockerImage({
      dockerfilePath,
      imageName: fullImageName,
      context,
      architecture,
      onOutput: (output: string) => {
        const cleanOutput = stripAnsiCodes(output);
        params.onProgress?.({ step: "build", output: cleanOutput });
      },
    });

    // Docker Login
    params.onProgress?.({ step: "auth", output: "Authenticating..." });
    await dockerLogin({
      registry: registryHost,
      username: credential.username,
      password: credential.password,
      onOutput: (output: string) => {
        const cleanOutput = stripAnsiCodes(output);
        params.onProgress?.({ step: "auth", output: cleanOutput });
      },
    });

    // Push Docker Image — wrapped in `withRetry` because `docker push` is
    // naturally idempotent (content-addressed layers) and transient registry
    // failures are common. We don't retry build (non-deterministic) or login
    // (fast, separate concern).
    params.onProgress?.({ step: "push", output: "Pushing Docker image..." });
    await withRetry(
      "snapshots.pushDockerImage",
      () =>
        pushDockerImage(fullImageName, (output: string) => {
          const cleanOutput = stripAnsiCodes(output);
          params.onProgress?.({ step: "push", output: cleanOutput });
        }),
      {
        ...this._retryConfig,
        onRetry: async (ctx) => {
          params.onProgress?.({
            step: "push",
            output: `Push failed (attempt ${ctx.attempt}), retrying in ${Math.round(ctx.delay)}ms…`,
          });
          await this._retryConfig?.onRetry?.(ctx);
        },
      },
    );

    params.onProgress?.({
      step: "register",
      output: "Registering snapshot...",
    });
    const snapshotData = await callApi(
      "snapshots.create",
      () =>
        api.createSnapshot({
          client: apiClient,
          body: { image: fullImageName, architecture },
        }),
      this._retryConfig,
    );

    let snapshotId = snapshotData.id;

    if (params.memorySnapshot) {
      // Create a memory snapshot from a sandbox
      params.onProgress?.({
        step: "memory-snapshot",
        output: "Creating sandbox...",
      });

      const cpuCount = 1;
      const memoryMb = 2048; // ~2GB
      const storageMb = 10240; // 10GB

      const sandboxResult = await callApi(
        "snapshots.createSandboxForMemorySnapshot",
        () =>
          api.createSandbox({
            body: {
              snapshot_id: snapshotData.id,
              ephemeral: true,
              millicpu: cpuCount * 1000,
              memory_bytes: memoryMb * 1024 * 1024,
              disk_bytes: storageMb * 1024 * 1024,
            },
          }),
        this._retryConfig,
      );

      params.onProgress?.({
        step: "memory-snapshot",
        output: "Starting sandbox...",
      });
      await callApi(
        "snapshots.startSandboxForMemorySnapshot",
        () =>
          api.startSandbox({
            client: apiClient,
            path: { id: sandboxResult.id },
          }),
        this._retryConfig,
      );

      params.onProgress?.({
        step: "memory-snapshot",
        output: "Waiting for sandbox to initialize...",
      });
      await sleep(10000);

      params.onProgress?.({
        step: "memory-snapshot",
        output: "Hibernating sandbox...",
      });
      const stopResult = await callApi(
        "snapshots.stopSandboxForMemorySnapshot",
        () =>
          api.stopSandbox({
            client: apiClient,
            path: { id: sandboxResult.id },
            body: { stop_type: "hibernate" },
          }),
        this._retryConfig,
      );

      if (stopResult.stop_reason !== "hibernated") {
        throw new Error(
          "Could not create memory snapshot, Sandbox was not hibernated",
        );
      }
      params.onProgress?.({
        step: "memory-snapshot",
        output: "Retrieving snapshot...",
      });
      const versionResult = await callApi(
        "snapshots.getSandboxVersionForMemorySnapshot",
        () =>
          api.getSandboxVersionByNumber({
            path: {
              sandbox_id: sandboxResult.id,
              number: stopResult.current_version_number,
            },
          }),
        this._retryConfig,
      );
      const snapshot = await callApi(
        "snapshots.getMemorySnapshot",
        () =>
          api.getSnapshot({
            client: apiClient,

            path: { id: versionResult.id },
          }),
        this._retryConfig,
      );

      snapshotId = snapshot.id;
    }

    // Create alias if needed
    if (params.alias) {
      const alias = params.alias;

      params.onProgress?.({
        step: "alias",
        output: "Creating alias...",
      });

      await callApi(
        "snapshots.alias",
        () =>
          api.aliasSnapshot({
            client: apiClient,
            path: { snapshot_id: snapshotId },
            body: { alias },
          }),
        this._retryConfig,
      );
    }

    return {
      snapshotId,
      alias: params.alias,
    };
  }
}

import * as api from "./api-clients/api/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { isLocalEnvironment } from "./configuration.js";
import { sleep } from "./utils.js";
import {
  buildDockerImage,
  dockerLogin,
  isDockerAvailable,
  pushDockerImage,
} from "./docker.js";
import { randomUUID } from "crypto";

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
  ) {}

  // ─── Public entry points ──────────────────────────────────────────────────

  async getById(id: string): Promise<Snapshot> {
    const result = await api.getSnapshot({
      client: this._apiClient,
      path: { id },
      throwOnError: true,
    });

    return result.data;
  }

  async getByAlias(alias: string): Promise<Snapshot> {
    const result = await api.getSnapshotByAlias({
      client: this._apiClient,
      path: { alias },
      throwOnError: true,
    });

    return result.data;
  }

  async list(): Promise<Snapshot[]> {
    const result = await api.listSnapshots({
      client: this._apiClient,
      throwOnError: true,
    });

    return result.data;
  }

  async alias(snapshotId: string, alias: string): Promise<void> {
    await api.aliasSnapshot({
      client: this._apiClient,
      path: { snapshot_id: snapshotId },
      body: { alias },
      throwOnError: true,
    });
  }

  async deleteById(id: string): Promise<void> {
    await api.deleteSnapshot({
      client: this._apiClient,
      path: { id },
      throwOnError: true,
    });
  }

  async deleteByAlias(alias: string): Promise<void> {
    // Ensure consistency with API
    const cleanAlias = alias.startsWith("@") ? alias.slice(1) : alias;

    await api.deleteSnapshotByAlias({
      client: this._apiClient,
      path: { alias: cleanAlias },
      throwOnError: true,
    });
  }

  /**
   * Create a snapshot from a Docker build context or a public Docker image.
   *
   * Pass `{ context, dockerfile?, alias?, onProgress?, memorySnapshot? }` to build from a Dockerfile.
   * Pass `{ image, alias?, onProgress? }` to register a public Docker image.
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

      const snapshotData = await api.createSnapshot({
        client: this._apiClient,
        body: { image: params.image, architecture: "amd64" },
        throwOnError: true,
      });

      // Create alias if needed
      if (params.alias) {
        params.onProgress?.({
          step: "alias",
          output: "Creating alias...",
        });

        await api.aliasSnapshot({
          client: this._apiClient,
          path: { snapshot_id: snapshotData.data.id },
          body: { alias: params.alias },
          throwOnError: true,
        });
      }

      return {
        snapshotId: snapshotData.data.id,
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

    const credential = await api.issueContainerRegistryCredential({
      client: this._apiClient,
      throwOnError: true,
    });
    const registryUrl = credential.data.registry_url;
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
      username: credential.data.username,
      password: credential.data.password,
      onOutput: (output: string) => {
        const cleanOutput = stripAnsiCodes(output);
        params.onProgress?.({ step: "auth", output: cleanOutput });
      },
    });

    // Push Docker Image
    params.onProgress?.({ step: "push", output: "Pushing Docker image..." });
    await pushDockerImage(fullImageName, (output: string) => {
      const cleanOutput = stripAnsiCodes(output);
      params.onProgress?.({ step: "push", output: cleanOutput });
    });

    params.onProgress?.({
      step: "register",
      output: "Registering snapshot...",
    });
    const snapshotData = await api.createSnapshot({
      client: apiClient,
      body: { image: fullImageName, architecture },
      throwOnError: true,
    });

    let snapshotId = snapshotData.data.id;

    if (params.memorySnapshot) {
      // Create a memory snapshot from a sandbox
      params.onProgress?.({
        step: "memory-snapshot",
        output: "Creating sandbox...",
      });

      const cpuCount = 1;
      const memoryMb = 2048; // ~2GB
      const storageMb = 10240; // 10GB

      const sandboxResult = await api.createSandbox({
        body: {
          snapshot_id: snapshotData.data.id,
          ephemeral: true,
          millicpu: cpuCount * 1000,
          memory_bytes: memoryMb * 1024 * 1024,
          disk_bytes: storageMb * 1024 * 1024,
        },
        throwOnError: true,
      });

      params.onProgress?.({
        step: "memory-snapshot",
        output: "Starting sandbox...",
      });
      await api.startSandbox({
        client: apiClient,
        path: { id: sandboxResult.data.id },
      });

      params.onProgress?.({
        step: "memory-snapshot",
        output: "Waiting for sandbox to initialize...",
      });
      await sleep(10000);

      params.onProgress?.({
        step: "memory-snapshot",
        output: "Hibernating sandbox...",
      });
      const stopResult = await api.stopSandbox({
        client: apiClient,
        path: { id: sandboxResult.data.id },
        body: { stop_type: "hibernate" },
        throwOnError: true,
      });

      if (stopResult.data.stop_reason !== "hibernated") {
        throw new Error(
          "Could not create memory snapshot, Sandbox was not hibernated",
        );
      }
      params.onProgress?.({
        step: "memory-snapshot",
        output: "Retrieving snapshot...",
      });
      const versionResult = await api.getSandboxVersionByNumber({
        path: {
          sandbox_id: sandboxResult.data.id,
          number: stopResult.data.current_version_number,
        },
        throwOnError: true,
      });
      const snapshot = await api.getSnapshot({
        throwOnError: true,
        path: { id: versionResult.data.id },
      });

      snapshotId = snapshot.data.id;
    }

    // Create alias if needed
    if (params.alias) {
      params.onProgress?.({
        step: "alias",
        output: "Creating alias...",
      });

      await api.aliasSnapshot({
        client: apiClient,
        path: { snapshot_id: snapshotId },
        body: { alias: params.alias },
        throwOnError: true,
      });
    }

    return {
      snapshotId,
      alias: params.alias,
    };
  }
}

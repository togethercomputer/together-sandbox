import * as api from "./api-clients/api/index.js";
import * as path from "path";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { getInferredRegistryUrl, isLocalEnvironment } from "./configuration.js";
import { base32Encode, sleep } from "./utils.js";
import { randomUUID } from "crypto";
import {
  buildDockerImage,
  createImageDockerfile,
  dockerLogin,
  isDockerAvailable,
  pushDockerImage,
} from "./docker.js";
import { rm } from "fs/promises";

export type SnapshotProgress = { output: string } & (
  | { step: "prepare" }
  | { step: "build" }
  | { step: "auth" }
  | { step: "push" }
  | { step: "register" }
  | { step: "memory-snapshot" }
  | { step: "alias" }
);

/**
 * Parameters for creating a snapshot
 */
export type CreateSnapshotParams = {
  /**
   * Optional alias to assign to the snapshot after creation.
   * Format: `tag` (namespace defaults to the directory name) or `namespace@tag`.
   * Only alphanumeric characters, dashes, and underscores are allowed; max 64
   * characters each.
   */
  alias?: string;

  /**
   * Boot the sandbox after building and hibernate it to capture a memory
   * snapshot. Currently disabled due to a Nydus bug.
   * @internal
   */
  memorySnapshot?: boolean;

  /**
   * Optional progress callback. Receives a short step label and a human-readable
   * message — useful for driving spinners or structured logging without coupling
   * the SDK to a specific UI library.
   */
  onProgress?: (event: SnapshotProgress) => void;
};

/**
 * Result of a successful snapshot creation.
 */
export interface CreateSnapshotResult {
  /** ID of the created (or memory-snapshotted) snapshot. */
  snapshotId: string;
  /** The full alias string that was applied (`namespace@tag`), if any. */
  alias?: string;
}

async function getMetaInfo(apiKey: string): Promise<{
  auth?: {
    scopes: Array<string>;
    team: string | null;
    version: string;
  };
}> {
  const response = await fetch("https://api.codesandbox.stream/meta/info", {
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
  });

  if (!response.ok) {
    throw new Error(
      `Request failed with status ${response.status}: ${response.statusText}`,
    );
  }

  const json = await response.json();

  return json;
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

function createAlias(defaultNamespace: string, alias: string) {
  const aliasParts = alias.split("@");

  if (aliasParts.length > 2) {
    throw new Error(
      `Alias name "${alias}" is invalid, must be in the format of name@tag`,
    );
  }

  const namespace = aliasParts.length === 2 ? aliasParts[0] : defaultNamespace;
  alias = aliasParts.length === 2 ? aliasParts[1] : alias;

  if (namespace.length > 64 || alias.length > 64) {
    throw new Error(
      `Alias name "${namespace}" or tag "${alias}" is too long, must be 64 characters or less`,
    );
  }

  if (!/^[a-zA-Z0-9-_]+$/.test(namespace) || !/^[a-zA-Z0-9-_]+$/.test(alias)) {
    throw new Error(
      `Alias name "${namespace}" or tag "${alias}" is invalid, must only contain upper/lower case letters, numbers, dashes and underscores`,
    );
  }

  return {
    namespace,
    alias,
  };
}

function extractImageName(image: string): string {
  // "ghcr.io/org/node:24" → "node"
  const withoutTag = image.split(":")[0];
  const parts = withoutTag.split("/");
  return parts[parts.length - 1];
}

/**
 * Snapshot build and management operations, accessed as `sdk.snapshots.*`.
 */
export class SnapshotsNamespace {
  constructor(
    private readonly _apiClient: ApiClient,
    private readonly _apiKey: string,
    private readonly _baseUrl: string,
  ) {}

  // ─── Public entry points ──────────────────────────────────────────────────

  /**
   * Build a Docker image from an existing Dockerfile and register it as a
   * Together Sandbox snapshot. The build context is the parent directory of
   * the Dockerfile.
   */
  async fromBuild(
    dockerContext: string,
    params?: CreateSnapshotParams & { dockerfile?: string },
  ): Promise<CreateSnapshotResult> {
    const dockerAvailable = await isDockerAvailable();
    if (!dockerAvailable) {
      console.error(
        "Docker is not available. Please install Docker to use beta build mode.",
      );
      process.exit(1);
    }

    const architecture: "amd64" | "arm64" =
      process.arch === "arm64" && isLocalEnvironment(this._baseUrl)
        ? "arm64"
        : "amd64";

    return this._buildAndRegister({
      dockerfilePath: params?.dockerfile,
      context: dockerContext,
      architecture,
      aliasDefaultNamespace: path.basename(dockerContext),
      cleanupFn: async () => {},
      params,
    });
  }

  /**
   * Pull a public Docker image and register it as a Together Sandbox snapshot.
   */
  async fromImage(
    image: string,
    params?: CreateSnapshotParams,
  ): Promise<CreateSnapshotResult> {
    const dockerAvailable = await isDockerAvailable();
    if (!dockerAvailable) {
      console.error(
        "Docker is not available. Please install Docker to use beta build mode.",
      );
      process.exit(1);
    }

    const { dockerfilePath, tmpDir } = await createImageDockerfile(image);
    const context = tmpDir;
    const architecture: "amd64" | "arm64" =
      process.arch === "arm64" && isLocalEnvironment(this._baseUrl)
        ? "arm64"
        : "amd64";

    return this._buildAndRegister({
      dockerfilePath,
      context,
      architecture,
      aliasDefaultNamespace: extractImageName(image),
      cleanupFn: () => rm(tmpDir, { recursive: true, force: true }),
      params,
    });
  }

  // ─── Private helpers ──────────────────────────────────────────────────────

  private async _buildAndRegister(opts: {
    dockerfilePath?: string;
    context: string;
    architecture: "amd64" | "arm64";
    aliasDefaultNamespace: string;
    cleanupFn: () => Promise<void>;
    params?: CreateSnapshotParams;
  }): Promise<CreateSnapshotResult> {
    const {
      dockerfilePath,
      context,
      architecture,
      aliasDefaultNamespace,
      cleanupFn,
      params,
    } = opts;

    try {
      const apiKey = this._apiKey;
      const apiClient = this._apiClient;

      const metaInfoResult = await getMetaInfo(apiKey);
      const teamId = metaInfoResult.auth?.team;

      if (!teamId) {
        throw new Error(
          "Failed to fetch team information for the provided API key. Please ensure your TOGETHER_API_KEY is correct and has access to a team.",
        );
      }

      const base32EncodedTeamId = base32Encode(teamId);

      const registry = getInferredRegistryUrl(this._baseUrl);
      const repository = base32EncodedTeamId;
      const imageName = `image-${randomUUID().toLowerCase()}`;
      const tag = randomUUID().toLowerCase();
      const fullImageName = `${registry}/${repository}/${imageName}:${tag}`;

      // Docker Build
      params?.onProgress?.({
        step: "prepare",
        output: "Preparing snapshot...",
      });
      params?.onProgress?.({ step: "build", output: "Building snapshot..." });
      await buildDockerImage({
        dockerfilePath,
        imageName: fullImageName,
        context,
        architecture,
        onOutput: (output: string) => {
          const cleanOutput = stripAnsiCodes(output);
          params?.onProgress?.({ step: "build", output: cleanOutput });
        },
      });

      // Docker Login
      params?.onProgress?.({ step: "auth", output: "Authenticating..." });
      await dockerLogin({
        registry: registry,
        username: "_token",
        password: apiKey,
        onOutput: (output: string) => {
          const cleanOutput = stripAnsiCodes(output);
          params?.onProgress?.({ step: "auth", output: cleanOutput });
        },
      });

      // Push Docker Image
      params?.onProgress?.({ step: "push", output: "Pushing Docker image..." });
      await pushDockerImage(fullImageName, (output: string) => {
        const cleanOutput = stripAnsiCodes(output);
        params?.onProgress?.({ step: "push", output: cleanOutput });
      });

      params?.onProgress?.({
        step: "register",
        output: "Registering snapshot...",
      });
      const snapshotData = await api.createSnapshot({
        client: apiClient,
        body: {
          image: {
            registry: registry,
            repository: repository,
            name: imageName,
            architecture: architecture,
            tag: tag,
          },
        },
        throwOnError: true,
      });

      let snapshotId = snapshotData.data.id;

      if (params?.memorySnapshot) {
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

      let alias;

      // Create alias if needed
      if (params?.alias) {
        params.onProgress?.({
          step: "alias",
          output: "Creating alias...",
        });

        const aliasParts = createAlias(aliasDefaultNamespace, params.alias);
        alias = `${aliasParts.namespace}@${aliasParts.alias}`;
        await api.aliasSnapshot({
          client: apiClient,
          path: { snapshot_id: snapshotId },
          body: { alias },
        });
      }

      return {
        snapshotId,
        alias,
      };
    } finally {
      await cleanupFn();
    }
  }
}

import * as api from "./api-clients/api/index.js";
import * as path from "path";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { getInferredRegistryUrl, isLocalEnvironment } from "./configuration.js";
import { base32Encode, sleep } from "./utils.js";
import { randomUUID } from "crypto";
import {
  buildDockerImage,
  dockerLogin,
  prepareDockerBuild,
  pushDockerImage,
} from "./docker.js";

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
 * Parameters for creating a snapshot.
 */
export interface CreateSnapshotParams {
  /**
   * Absolute or relative path to the project directory to build the snapshot
   * from. A Dockerfile is located in the root or `.codesandbox/` directory; if
   * neither exists a default `FROM node:24` Dockerfile is generated.
   */
  directory: string;

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
   *
   * @example
   * ```typescript
   * sdk.snapshots.create({
   *   directory: "./my-app",
   *   onProgress: (step, msg) => console.log(`[${step}] ${msg}`),
   * });
   * ```
   */
  onProgress?: (event: SnapshotProgress) => void;
}

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
  //   \[         = literal “[”
  //   [0-?]*     = any parameter bytes (digits, ;, ?)
  //   [ -/]*     = any intermediate bytes (space through /)
  //   [@-~]      = final byte ( @ A–Z [ \ ] ^ _ ` a–z { | } ~ )
  const CSI_REGEX = /\x1B\[[0-?]*[ -/]*[@-~]/g;
  return str.replace(CSI_REGEX, "");
}

function createAlias(directory: string, alias: string) {
  const aliasParts = alias.split("@");

  if (aliasParts.length > 2) {
    throw new Error(
      `Alias name "${alias}" is invalid, must be in the format of name@tag`,
    );
  }

  const namespace =
    aliasParts.length === 2 ? aliasParts[0] : path.basename(directory);
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

/**
 * Snapshot build and management operations, accessed as `sdk.snapshots.*`.
 */
export class SnapshotsNamespace {
  constructor(
    private readonly _apiClient: ApiClient,
    private readonly _apiKey: string,
    private readonly _baseUrl: string,
  ) {}

  /**
   * Build a Docker image from a local directory and register it as a Together
   * Sandbox snapshot.
   *
   * @example
   * ```typescript
   * const { snapshotId } = await sdk.snapshots.create({
   *   directory: "./my-app",
   *   alias: "my-app@latest",
   *   onProgress: (step, msg) => console.log(`[${step}] ${msg}`),
   * });
   * ```
   */
  async create(params: CreateSnapshotParams): Promise<CreateSnapshotResult> {
    let dockerFileCleanupFn: (() => Promise<void>) | undefined;

    try {
      const apiKey = this._apiKey;
      const apiClient = this._apiClient;
      const resolvedDirectory = path.resolve(params.directory);

      // New api to get the registry + repository (First part of path)
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

      let architecture: "amd64" | "arm64" | undefined = "amd64";
      // For dev environments with arm64 (Apple Silicon), use arm64 architecture
      if (process.arch === "arm64" && isLocalEnvironment(this._baseUrl)) {
        console.log("Using arm64 architecture for Docker build");
        architecture = "arm64";
      }

      // Prepare Docker Build
      params.onProgress?.({ step: "prepare", output: "Preparing snapshot..." });

      let dockerfilePath: string;

      try {
        const result = await prepareDockerBuild(
          resolvedDirectory,
          (output: string) => {
            params.onProgress?.({ step: "prepare", output });
          },
        );
        dockerFileCleanupFn = result.cleanupFn;
        dockerfilePath = result.dockerfilePath;
      } catch (error) {
        throw error;
      }

      // Docker Build
      params.onProgress?.({ step: "build", output: "Building snapshot..." });
      await buildDockerImage({
        dockerfilePath,
        imageName: fullImageName,
        context: resolvedDirectory,
        architecture,
        onOutput: (output: string) => {
          const cleanOutput = stripAnsiCodes(output);
          params.onProgress?.({ step: "build", output: cleanOutput });
        },
      });
      // Docker Login

      params.onProgress?.({ step: "auth", output: "Authenticating..." });
      await dockerLogin({
        registry: registry,
        username: "_token",
        password: apiKey,
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

      let alias;

      // Create alias if needed
      if (params.alias) {
        params.onProgress?.({
          step: "alias",
          output: "Creating alias...",
        });

        const aliasParts = createAlias(resolvedDirectory, params.alias);
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
      if (dockerFileCleanupFn) {
        await dockerFileCleanupFn();
      }
    }
  }
}

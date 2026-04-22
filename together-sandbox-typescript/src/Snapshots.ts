import * as api from "./api-clients/api/index.js";
import * as path from "path";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { getInferredRegistryUrl, isLocalEnvironment } from "./configuration.js";
import { base32Encode, sleep } from "./utils.js";
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

export type ImageReference = {
  registry?: string;
  repository?: string;
  name: string;
  tag?: string;
};

export function parseImageReference(image: string): ImageReference {
  // Split tag from the end
  let tag: string | undefined;
  let withoutTag = image;

  const tagIndex = image.lastIndexOf(":");
  if (tagIndex !== -1) {
    // Check if the part after ':' contains '/' — if so, it's not a tag
    // (e.g., "registry.example.com:5000/org/app" shouldn't treat ":5000" as a tag)
    const afterColon = image.slice(tagIndex + 1);
    if (!afterColon.includes("/")) {
      tag = afterColon;
      withoutTag = image.slice(0, tagIndex);
    }
  }

  // Split path segments
  const parts = withoutTag.split("/");

  let registry: string | undefined;
  let repository: string | undefined;
  let name: string;

  if (parts.length === 1) {
    // Just "node" or "ubuntu"
    name = parts[0];
  } else if (parts.length === 2) {
    // Either "org/myapp" or "registry.example.com/myapp"
    const firstPart = parts[0];
    if (firstPart.includes(".") || firstPart.includes(":")) {
      // It's a registry
      registry = firstPart;
      name = parts[1];
    } else {
      // It's a repository
      repository = firstPart;
      name = parts[1];
    }
  } else if (parts.length >= 3) {
    // "registry/org/myapp" or more
    const firstPart = parts[0];
    if (firstPart.includes(".") || firstPart.includes(":")) {
      // First part is registry
      registry = firstPart;
      repository = parts[1];
      name = parts[2];
    } else {
      // No registry, first part is repository
      repository = firstPart;
      name = parts[1];
    }
  } else {
    throw new Error(`Invalid image reference: ${image}`);
  }

  return {
    registry,
    repository,
    name,
    tag,
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

  // ─── Public entry points ──────────────────────────────────────────────────

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
      const imageRef = parseImageReference(params.image);
      const extractedName = imageRef.name;

      params.onProgress?.({
        step: "register",
        output: "Registering snapshot...",
      });

      const snapshotData = await api.createSnapshot({
        client: this._apiClient,
        body: {
          image: {
            registry: imageRef.registry,
            repository: imageRef.repository,
            name: imageRef.name,
            tag: imageRef.tag,
            architecture: "amd64",
          },
        },
        throwOnError: true,
      });

      let alias;

      // Create alias if needed
      if (params.alias) {
        params.onProgress?.({
          step: "alias",
          output: "Creating alias...",
        });

        const aliasParts = createAlias(extractedName, params.alias);
        alias = `${aliasParts.namespace}@${aliasParts.alias}`;
        await api.aliasSnapshot({
          client: this._apiClient,
          path: { snapshot_id: snapshotData.data.id },
          body: { alias },
          throwOnError: true,
        });
      }

      return {
        snapshotId: snapshotData.data.id,
        alias,
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
    const aliasDefaultNamespace = path.basename(params.context);
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

      const aliasParts = createAlias(aliasDefaultNamespace, params.alias);
      alias = `${aliasParts.namespace}@${aliasParts.alias}`;
      await api.aliasSnapshot({
        client: apiClient,
        path: { snapshot_id: snapshotId },
        body: { alias },
        throwOnError: true,
      });
    }

    return {
      snapshotId,
      alias,
    };
  }
}

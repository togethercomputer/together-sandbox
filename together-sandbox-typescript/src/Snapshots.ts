import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import * as api from "./api-clients/api/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { isLocalEnvironment } from "./configuration.js";
import { callApi, withRetry } from "./utils.js";
import { Page } from "./pagination.js";
import {
  buildDockerImage,
  dockerLogin,
  isDockerAvailable,
  pushDockerImage,
} from "./docker.js";
import { RemoteImageBuilderClient } from "./RemoteImageBuilder.js";
import { randomUUID } from "crypto";
import type { RetryConfig } from "./types.js";

export type SnapshotProgress = { output: string } & (
  | { step: "prepare" }
  | { step: "build" }
  | { step: "auth" }
  | { step: "push" }
  | { step: "register" }
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
  /** Arbitrary key/value labels to attach to the snapshot. */
  tags?: Record<string, string>;
  /** Seconds after creation before the snapshot is automatically retired. */
  ttl?: number;
};

export type CreateImageSnapshotParams = {
  image: string;
  alias?: string;
  onProgress?: (event: SnapshotProgress) => void;
  /** Arbitrary key/value labels to attach to the snapshot. */
  tags?: Record<string, string>;
  /** Seconds after creation before the snapshot is automatically retired. */
  ttl?: number;
};
export type CreateSnapshotParams =
  | CreateContextSnapshotParams
  | CreateImageSnapshotParams;

/**
 * Result of a successful snapshot creation.
 */
export interface CreateSnapshotResult {
  /** ID of the created snapshot. */
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
    private readonly _apiKey: string,
    private readonly _retryConfig?: RetryConfig,
  ) {}

  // ─── Public entry points ──────────────────────────────────────────────────

  async getById(id: string): Promise<Snapshot> {
    const result = await callApi(
      "api.snapshots.getById",
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
      "api.snapshots.getByAlias",
      () =>
        api.getSnapshotByAlias({
          client: this._apiClient,
          path: { alias },
        }),
      this._retryConfig,
    );

    return result;
  }

  /**
   * List snapshots.
   *
   * Returns a {@link Page} that is async-iterable across all pages — iterate it
   * directly to walk every snapshot, or use `getNextPage()` / `nextCursor` for
   * manual page-by-page control.
   *
   * @param options.limit Max items per page (1–100, default 20).
   * @param options.cursor Resume from a cursor returned by a previous page's
   *   {@link Page.nextCursor} (omit to start from the first page).
   * @param options.excludeRetired When true, retired snapshots are excluded
   *   (default false — retired snapshots are included).
   * @param options.tags Filter by tags; matches snapshots whose tags contain
   *   all the given pairs.
   */
  async list(options?: {
    limit?: number;
    cursor?: string;
    excludeRetired?: boolean;
    tags?: Record<string, string>;
  }): Promise<Page<Snapshot>> {
    const fetchPage = async (cursor?: string): Promise<Page<Snapshot>> => {
      const result = await callApi(
        "api.snapshots.list",
        () =>
          api.listSnapshots({
            client: this._apiClient,
            query: {
              limit: options?.limit,
              cursor,
              exclude_retired: options?.excludeRetired,
              tags: options?.tags,
            },
          }),
        this._retryConfig,
      );
      return new Page<Snapshot>(result.data, result.next_cursor, fetchPage);
    };

    return fetchPage(options?.cursor);
  }

  async alias(snapshotId: string, alias: string): Promise<void> {
    await callApi(
      "api.snapshots.alias",
      () =>
        api.aliasSnapshot({
          client: this._apiClient,
          path: { snapshot_id: snapshotId },
          body: { alias },
        }),
      this._retryConfig,
    );
  }

  /**
   * Retire a snapshot by id and return the retired snapshot.
   *
   * Once retired, the snapshot can no longer be used to create new sandboxes,
   * and it is eventually deleted, but only once no sandbox still references
   * it.
   */
  async retire(id: string): Promise<Snapshot> {
    const result = await callApi(
      "api.snapshots.retire",
      () =>
        api.retireSnapshot({
          client: this._apiClient,
          path: { id },
        }),
      this._retryConfig,
    );

    return result;
  }

  /**
   * Create a snapshot from a Docker build context or a public Docker image.
   *
   * Pass `{ context, dockerfile?, alias?, onProgress? }` to build from a Dockerfile.
   * Pass `{ image, alias?, onProgress? }` to register a public Docker image.
   *
   * @note The `snapshots.create` operation is not idempotent: retrying on a 500 error
   * after the snapshot has been created will register a duplicate. If you are using
   * retry configuration, consider excluding this operation via:
   * `shouldRetry: ({ operation }) => operation !== 'snapshots.create'`
   */
  async create(params: CreateSnapshotParams): Promise<CreateSnapshotResult> {
    // Build from context — defaults to the remote image-builder service.
    // Set `TOGETHER_LOCAL_BUILD=1` to fall back to the legacy local Docker
    // build + push flow (`_buildAndRegister`), which mirrors the Python SDK.
    let result: { image: string; architecture: "amd64" | "arm64" };
    if ("context" in params && process.env.TOGETHER_LOCAL_BUILD === "1") {
      const dockerAvailable = await isDockerAvailable();
      if (!dockerAvailable) {
        throw new Error(
          "Docker is not available. Please install Docker to use local build mode (TOGETHER_LOCAL_BUILD=1).",
        );
      }
      result = await this._buildAndRegister(params);
    } else if ("context" in params) {
      result = await this._buildRemotely(params);
    } else {
      result = await this._buildRemotelyFromImage(params);
    }

    params.onProgress?.({
      step: "register",
      output: "Registering snapshot...",
    });
    const snapshotData = await callApi(
      "api.snapshots.create",
      () =>
        api.createSnapshot({
          client: this._apiClient,
          body: {
            image: result.image,
            architecture: result.architecture,
            ttl: params.ttl,
            tags: params.tags,
          },
        }),
      this._retryConfig,
    );

    const snapshotId = snapshotData.id;

    // Create alias if needed
    if (params.alias) {
      const alias = params.alias;

      params.onProgress?.({
        step: "alias",
        output: "Creating alias...",
      });

      await callApi(
        "api.snapshots.alias",
        () =>
          api.aliasSnapshot({
            client: this._apiClient,
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

  // ─── Private helpers ──────────────────────────────────────────────────────
  /**
   * Build a Docker image from a public image reference via the remote
   * image-builder service.
   *
   * Creates a temporary directory named after the image (so `_buildRemotely`
   * derives a meaningful image name from `path.basename(contextDir)`) and
   * writes a single-line Dockerfile of the form `FROM <image>` into it. The
   * temp directory is removed on exit regardless of build outcome.
   */
  private async _buildRemotelyFromImage(
    params: CreateImageSnapshotParams,
  ): Promise<{ image: string; architecture: "amd64" | "arm64" }> {
    // Derive a folder name from the image's last path component, stripped of
    // any tag/digest. e.g. "ghcr.io/foo/bar:latest" -> "bar",
    // "node:22" -> "node". The fallback to "image" guards against
    // pathological inputs that strip to an empty string.
    const lastSegment = params.image.split("/").pop() ?? "";
    const imageNameSlug =
      lastSegment
        .split("@")[0]
        .split(":")[0]
        .toLowerCase()
        .replace(/_/g, "-") || "image";

    const tmpParent = await fs.promises.mkdtemp(
      path.join(os.tmpdir(), "together-sandbox-"),
    );
    const contextDir = path.join(tmpParent, imageNameSlug);
    try {
      await fs.promises.mkdir(contextDir, { recursive: true });
      await fs.promises.writeFile(
        path.join(contextDir, "Dockerfile"),
        `FROM ${params.image}\n`,
      );

      return await this._buildRemotely({
        context: contextDir,
        alias: params.alias,
        onProgress: params.onProgress,
      });
    } finally {
      await fs.promises.rm(tmpParent, { recursive: true, force: true });
    }
  }
  /**
   * Build a Docker image using the remote image-builder service.
   *
   * Mirrors the Python SDK's `_build_image_remotely`: derives the
   * image-builder URL from the configured base URL by replacing
   * `api.bartender.` with `builder.`, uses the SDK's API key as the
   * auth token, and returns the image reference and architecture that should
   * be passed to `snapshots.create`.
   */
  private async _buildRemotely(
    params: CreateContextSnapshotParams,
  ): Promise<{ image: string; architecture: "amd64" | "arm64" }> {
    const ibApiUrl = this._baseUrl.replace("api.bartender.", "builder.");

    const contextDir = path.resolve(params.context);
    const dockerfilePath = params.dockerfile
      ? path.resolve(params.dockerfile)
      : path.join(contextDir, "Dockerfile");
    const dockerfileRel = path.relative(contextDir, dockerfilePath);

    // Unique name/tag per build so concurrent builds can't collide on the
    // same ref (the namespace is shared, derived from the auth token).
    const imageName = `image-${randomUUID().toLowerCase()}`;
    const imageTag = randomUUID().toLowerCase();
    const imageRef = `${imageName}:${imageTag}`;

    const emit = (output: string) =>
      params.onProgress?.({ step: "build", output: stripAnsiCodes(output) });

    const ibClient = new RemoteImageBuilderClient({
      apiUrl: ibApiUrl,
      token: this._apiKey,
      logger: {
        debug: emit,
        warning: emit,
      },
    });

    params.onProgress?.({
      step: "prepare",
      output: "Starting remote build ...",
    });
    const imageRefStr = await ibClient.build({
      contextDir,
      imageName: imageRef,
      dockerfile: dockerfileRel,
      nydus: true,
    });

    const archEnv = process.env.TOGETHER_REMOTE_ARCHITECTURE;
    let architecture: "amd64" | "arm64";
    if (archEnv) {
      if (archEnv !== "amd64" && archEnv !== "arm64") {
        throw new Error(
          `Invalid TOGETHER_REMOTE_ARCHITECTURE=${JSON.stringify(archEnv)}; ` +
            `expected one of: ["amd64","arm64"]`,
        );
      }
      architecture = archEnv;
    } else {
      architecture = "amd64";
    }

    return {
      image: imageRefStr,
      architecture,
    };
  }

  private async _buildAndRegister(
    params: CreateContextSnapshotParams,
  ): Promise<{ image: string; architecture: "amd64" | "arm64" }> {
    const architecture: "amd64" | "arm64" =
      process.arch === "arm64" && isLocalEnvironment(this._baseUrl)
        ? "arm64"
        : "amd64";
    const dockerfilePath = params.dockerfile;
    const context = params.context;

    const credential = await callApi(
      "api.snapshots.issueContainerRegistryCredential",
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

    return {
      image: fullImageName,
      architecture,
    };
  }
}

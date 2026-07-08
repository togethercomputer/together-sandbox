import * as api from "./api-clients/api/index.js";
import {
  createClient as createSandboxClient,
  createConfig as createSandboxConfig,
} from "./api-clients/sandbox/client/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { Sandbox, type StartOptions } from "./Sandbox.js";
import {
  type SandboxInfo,
  type CreateSandboxParams,
  type RetryConfig,
} from "./types.js";
import { camelCaseKeys, callApi } from "./utils.js";
import { describeLifecycleFailure } from "./lifecycle.js";
import { Page } from "./pagination.js";

/**
 * Extract the agent connection details from the Sandbox model.
 */
function resolveConnectionDetails(sandbox: SandboxInfo): {
  url: string;
  token: string;
} {
  if (!sandbox.agentUrl || !sandbox.agentToken)
    throw new Error("Sandbox has no agent connection details");
  return { url: sandbox.agentUrl, token: sandbox.agentToken };
}

/**
 * A sandbox record as returned by the management API list/get endpoints.
 *
 * Named separately from the {@link Sandbox} runtime class (a wired client) —
 * this is the raw metadata model.
 */
export type SandboxRecord = api.Sandbox;

// Default sandbox resource allocation. Match the CLI/snapshot helper.
export const DEFAULT_MILLICPU = 1000; // 1 vCPU
export const DEFAULT_MEMORY_BYTES = 2048 * 1024 * 1024; // 2 GiB
export const DEFAULT_DISK_BYTES = 10240 * 1024 * 1024; // 10 GiB

/**
 * Sandbox lifecycle operations, accessed as `sdk.sandboxes.*`.
 */
export class SandboxesNamespace {
  constructor(
    private readonly _apiClient: ApiClient,
    private readonly _retryConfig?: RetryConfig,
  ) {}

  /**
   * Create a new sandbox (does not start the VM).
   */
  async create(params: CreateSandboxParams): Promise<SandboxInfo> {
    const data = await callApi(
      "api.createSandbox",
      () =>
        api.createSandbox({
          client: this._apiClient,
          body: {
            id: params.id,
            snapshot_id: params.snapshotId,
            snapshot_alias: params.snapshotAlias,
            ephemeral: params.ephemeral,
            millicpu: params.millicpu ?? DEFAULT_MILLICPU,
            memory_bytes: params.memoryBytes ?? DEFAULT_MEMORY_BYTES,
            disk_bytes: params.diskBytes ?? DEFAULT_DISK_BYTES,
          },
        }),
      this._retryConfig,
    );
    return camelCaseKeys(data);
  }

  /**
   * List sandboxes.
   *
   * Returns a {@link Page} that is async-iterable across all pages — iterate it
   * directly to walk every sandbox, or use `getNextPage()` / `nextCursor` for
   * manual page-by-page control.
   *
   * @param options.limit Max items per page (1–100, default 20).
   * @param options.projectId Filter to a single project.
   * @param options.cursor Resume from a cursor returned by a previous page's
   *   {@link Page.nextCursor} (omit to start from the first page).
   */
  async list(options?: {
    limit?: number;
    projectId?: string;
    cursor?: string;
  }): Promise<Page<SandboxInfo>> {
    const fetchPage = async (cursor?: string): Promise<Page<SandboxInfo>> => {
      const result = await callApi(
        "api.listSandboxes",
        () =>
          api.listSandboxes({
            client: this._apiClient,
            query: {
              limit: options?.limit,
              cursor,
              project_id: options?.projectId,
            },
          }),
        this._retryConfig,
      );
      return new Page<SandboxInfo>(
        result.data.map((s) => camelCaseKeys(s)),
        result.next_cursor,
        fetchPage,
      );
    };

    return fetchPage(options?.cursor);
  }

  /**
   * Fetch a single sandbox by id. Returns the camelCased {@link SandboxInfo}
   * metadata, consistent with {@link list}.
   */
  async get(sandboxId: string): Promise<SandboxInfo> {
    const data = await callApi(
      "api.getSandbox",
      () =>
        api.getSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
        }),
      this._retryConfig,
      `for sandbox '${sandboxId}'`,
    );

    return camelCaseKeys(data);
  }

  /**
   * Start a VM for the given sandbox ID and return a {@link Sandbox}
   * with a fully wired sandbox client.
   */
  async start(sandboxId: string, options?: StartOptions): Promise<Sandbox> {
    const body =
      options?.versionNumber !== undefined
        ? { version_number: options.versionNumber }
        : undefined;

    await callApi(
      "api.startSandbox",
      () =>
        api.startSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
          body,
        }),
      this._retryConfig,
    );

    const waitResult = await callApi(
      "api.waitForSandbox",
      () =>
        api.waitForSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
        }),
      this._retryConfig,
    );

    if (waitResult.status !== "running") {
      throw new Error(describeLifecycleFailure(waitResult, "running"));
    }

    const finalData = camelCaseKeys(waitResult);
    const { url, token } = resolveConnectionDetails(finalData);
    const sandboxClient = createSandboxClient(
      createSandboxConfig({
        baseUrl: url,
        headers: { Authorization: `Bearer ${token}` },
      }),
    );

    // Add error interceptor to handle non-retryable errors
    sandboxClient.interceptors.error.use((error) => error);

    return new Sandbox(
      finalData,
      sandboxClient,
      this._apiClient,
      this._retryConfig,
    );
  }

  /**
   * Hibernate (suspend) a VM by sandbox ID.
   */
  async hibernate(sandboxId: string): Promise<void> {
    await callApi(
      "api.stopSandbox",
      () =>
        api.stopSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
          body: { stop_type: "hibernate" },
        }),
      this._retryConfig,
    );
    const waitResult = await callApi(
      "api.waitForSandbox",
      () =>
        api.waitForSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
        }),
      this._retryConfig,
    );

    if (waitResult.status !== "stopped") {
      throw new Error(describeLifecycleFailure(waitResult, "stopped"));
    }
  }

  /**
   * Shut down a VM by sandbox ID.
   */
  async shutdown(sandboxId: string): Promise<void> {
    await callApi(
      "api.stopSandbox",
      () =>
        api.stopSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
          body: { stop_type: "shutdown" },
        }),
      this._retryConfig,
    );
    const waitResult = await callApi(
      "api.waitForSandbox",
      () =>
        api.waitForSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
        }),
      this._retryConfig,
    );

    if (waitResult.status !== "stopped") {
      throw new Error(describeLifecycleFailure(waitResult, "stopped"));
    }
  }
}

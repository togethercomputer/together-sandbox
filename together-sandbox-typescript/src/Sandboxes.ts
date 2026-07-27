import * as api from "./api-clients/api/index.js";
import {
  createClient as createSandboxClient,
  createConfig as createSandboxConfig,
} from "./api-clients/sandbox/client/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { Sandbox } from "./Sandbox.js";
import {
  type SandboxInfo,
  type SandboxStatus,
  type CreateSandboxParams,
  type TerminationSnapshotParams,
  type RetryConfig,
} from "./types.js";
import {
  camelCaseKeys,
  callApi,
  terminationPolicyBody,
  terminationSnapshotBody,
} from "./utils.js";
import { describeLifecycleFailure } from "./lifecycle.js";
import { Page } from "./pagination.js";

/**
 * Extract the agent connection details from the Sandbox model.
 */
function resolveConnectionDetails(sandbox: SandboxInfo): {
  url: string;
  token: string;
} {
  if (!sandbox.agent?.url || !sandbox.agent?.token)
    throw new Error("Sandbox has no agent connection details");
  return { url: sandbox.agent.url, token: sandbox.agent.token };
}

/**
 * Wait for a sandbox to reach "running", wire up its client, and return a
 * connected {@link Sandbox}.
 */
async function connectRunningSandbox(
  sandboxId: string,
  apiClient: ApiClient,
  retryConfig: RetryConfig | undefined,
): Promise<Sandbox> {
  const waitResult = await callApi(
    "api.waitForSandbox",
    () =>
      api.waitForSandbox({
        client: apiClient,
        path: { id: sandboxId },
      }),
    retryConfig,
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

  sandboxClient.interceptors.error.use((error) => error);

  return new Sandbox(finalData, sandboxClient, apiClient, retryConfig);
}

// Default sandbox resource allocation. Match the CLI/snapshot helper.
export const DEFAULT_CPU = 1; // 1 vCPU (cores)
export const DEFAULT_MEMORY_BYTES = 2048 * 1024 * 1024; // 2 GiB

/**
 * Sandbox lifecycle operations, accessed as `sdk.sandboxes.*`.
 */
export class SandboxesNamespace {
  constructor(
    private readonly _apiClient: ApiClient,
    private readonly _retryConfig?: RetryConfig,
  ) {}

  /**
   * Create a sandbox and wait for it to be running, returning a connected {@link Sandbox}.
   */
  async create(params: CreateSandboxParams = {}): Promise<Sandbox> {
    const data = await callApi(
      "api.createSandbox",
      () =>
        api.createSandbox({
          client: this._apiClient,
          body: {
            snapshot_id: params.snapshotId,
            snapshot_alias: params.snapshotAlias,
            cpu: params.cpu ?? DEFAULT_CPU,
            memory_bytes: params.memoryBytes ?? DEFAULT_MEMORY_BYTES,
            ttl: params.ttl,
            tags: params.tags,
            termination_policy: terminationPolicyBody(params.terminationPolicy) ?? undefined,
          },
        }),
      this._retryConfig,
    );

    return connectRunningSandbox(data.id, this._apiClient, this._retryConfig);
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
   * @param options.statuses Filter by status; matches sandboxes in any of the
   *   given statuses.
   * @param options.tags Filter by tags; matches sandboxes whose tags contain
   *   all the given pairs.
   */
  async list(options?: {
    limit?: number;
    projectId?: string;
    statuses?: SandboxStatus[];
    tags?: Record<string, string>;
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
              "statuses[]": options?.statuses,
              tags: options?.tags,
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

    return fetchPage();
  }

  /**
   * Terminate a VM by sandbox ID. After this the sandbox is terminal and cannot
   * be used again.
   *
   * `snapshot` overrides what the sandbox's stored termination policy would
   * snapshot for this teardown (omit to use the stored policy; `null` to make
   * it ephemeral). The produced snapshot is aliased as `sandbox:<sandbox id>`
   * plus any `snapshot.aliases`.
   */
  async terminate(
    sandboxId: string,
    options: {
      snapshot?: TerminationSnapshotParams | null;
    } = {},
  ): Promise<void> {
    await callApi(
      "api.terminateSandbox",
      () =>
        api.terminateSandbox({
          client: this._apiClient,
          path: { id: sandboxId },
          body: {
            snapshot: terminationSnapshotBody(options.snapshot),
          },
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

    if (waitResult.status !== "terminated") {
      throw new Error(describeLifecycleFailure(waitResult, "terminated"));
    }
  }

  /**
   * Hibernate (suspend) a VM by sandbox ID — a terminate that snapshots both
   * the filesystem and memory.
   */
  async hibernate(sandboxId: string): Promise<void> {
    await this.terminate(sandboxId, {
      snapshot: { memory: true },
    });
  }

  /**
   * Shut down a VM by sandbox ID — a terminate that snapshots the filesystem.
   */
  async shutdown(sandboxId: string): Promise<void> {
    await this.terminate(sandboxId, {
      snapshot: { memory: false },
    });
  }
}

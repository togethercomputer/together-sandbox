import * as api from "./api-clients/api/index.js";
import {
  createClient as createSandboxClient,
  createConfig as createSandboxConfig,
} from "./api-clients/sandbox/client/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { Sandbox, type StartOptions } from "./Sandbox.js";
import { type SandboxInfo, type CreateSandboxParams } from "./types.js";
import { camelCaseKeys } from "./utils.js";

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
 * Sandbox lifecycle operations, accessed as `sdk.sandboxes.*`.
 */
export class SandboxesNamespace {
  constructor(private readonly _apiClient: ApiClient) {}

  /**
   * Create a new sandbox (does not start the VM).
   */
  async create(params: CreateSandboxParams): Promise<SandboxInfo> {
    const result = await api.createSandbox({
      client: this._apiClient,
      body: {
        id: params.id,
        snapshot_id: params.snapshotId,
        snapshot_alias: params.snapshotAlias,
        ephemeral: params.ephemeral,
        millicpu: params.millicpu,
        memory_bytes: params.memoryBytes,
        disk_bytes: params.diskBytes,
      },
      throwOnError: true,
    });
    return camelCaseKeys(result.data);
  }

  /**
   * Start a VM for the given sandbox ID and return a {@link Sandbox}
   * with a fully wired sandbox client.
   */
  async start(sandboxId: string, options?: StartOptions): Promise<Sandbox> {
    const result = await api.startSandbox({
      client: this._apiClient,
      path: { id: sandboxId },
      body:
        options?.versionNumber !== undefined
          ? { version_number: options.versionNumber }
          : undefined,
      throwOnError: true,
    });
    const data = camelCaseKeys(result.data);

    const waitResult = await api.waitForSandbox({
      client: this._apiClient,
      path: { id: sandboxId },
      throwOnError: true,
    });

    if (waitResult.data.status !== "running") {
      throw new Error(
        `Sandbox did not reach its running state, it is ${waitResult.data.status}, please try again`,
      );
    }

    const finalData = camelCaseKeys(waitResult.data);
    const { url, token } = resolveConnectionDetails(finalData);
    const sandboxClient = createSandboxClient(
      createSandboxConfig({
        baseUrl: url,
        headers: { Authorization: `Bearer ${token}` },
      }),
    );

    return new Sandbox(finalData, sandboxClient, this._apiClient);
  }

  /**
   * Hibernate (suspend) a VM by sandbox ID.
   */
  async hibernate(sandboxId: string): Promise<void> {
    await api.stopSandbox({
      client: this._apiClient,
      path: { id: sandboxId },
      body: { stop_type: "hibernate" },
      throwOnError: true,
    });
    const waitResult = await api.waitForSandbox({
      client: this._apiClient,
      path: { id: sandboxId },
      throwOnError: true,
    });

    if (waitResult.data.status !== "stopped") {
      throw new Error(
        `Sandbox did not reach its stopped state, it is ${waitResult.data.status}, please try again`,
      );
    }
  }

  /**
   * Shut down a VM by sandbox ID.
   */
  async shutdown(sandboxId: string): Promise<void> {
    await api.stopSandbox({
      client: this._apiClient,
      path: { id: sandboxId },
      body: { stop_type: "shutdown" },
      throwOnError: true,
    });
    const waitResult = await api.waitForSandbox({
      client: this._apiClient,
      path: { id: sandboxId },
      throwOnError: true,
    });

    if (waitResult.data.status !== "stopped") {
      throw new Error(
        `Sandbox did not reach its stopped state, it is ${waitResult.data.status}, please try again`,
      );
    }
  }
}

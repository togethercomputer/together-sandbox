import * as api from "./api-clients/api/index.js";
import {
  createClient as createSandboxClient,
  createConfig as createSandboxConfig,
} from "./api-clients/sandbox/client/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import { Sandbox, type StartOptions } from "./Sandbox.js";
import type { Sandbox as SandboxModel } from "./api-clients/api/types.gen.js";

/**
 * Extract the agent connection details from the Sandbox model.
 */
function resolveConnectionDetails(sandbox: SandboxModel): {
  url: string;
  token: string;
} {
  if (!sandbox.agent_url || !sandbox.agent_token)
    throw new Error("Sandbox has no agent connection details");
  return { url: sandbox.agent_url, token: sandbox.agent_token };
}

/**
 * Sandbox lifecycle operations, accessed as `sdk.sandboxes.*`.
 */
export class SandboxesNamespace {
  constructor(private readonly _apiClient: ApiClient) {}

  /**
   * Start a VM for the given sandbox ID and return a {@link Sandbox}
   * with a fully wired sandbox client.
   */
  async start(sandboxId: string, options?: StartOptions): Promise<Sandbox> {
    const result = await api.startSandbox({
      client: this._apiClient,
      path: { id: sandboxId },
      body: options?.startOptions,
      throwOnError: true,
    });
    const data = result.data;
    const { url, token } = resolveConnectionDetails(data);

    const sandboxClient = createSandboxClient(
      createSandboxConfig({
        baseUrl: url,
        headers: { Authorization: `Bearer ${token}` },
      }),
    );

    return new Sandbox(data, sandboxClient, this._apiClient);
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
  }
}

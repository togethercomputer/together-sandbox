import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock all generated api-client modules before any other import so the module
// graph resolves without the actual generated files (which may not exist in CI).
vi.mock("./api-clients/api/index.js", () => ({}));
vi.mock("./api-clients/api/client/index.js", () => ({}));
vi.mock("./api-clients/sandbox/client/index.js", () => ({
  createClient: vi.fn(() => ({
    interceptors: { error: { use: vi.fn() } },
  })),
  createConfig: vi.fn(() => ({})),
}));
vi.mock("./Sandbox.js", () => ({
  Sandbox: class {
    id: string;
    constructor(data: { id: string }) {
      this.id = data.id;
    }
  },
}));

// Mock callApi so tests control what each API call returns without needing
// real HTTP clients. This mirrors the approach used in utils.test.ts.
vi.mock("./utils.js", async (importOriginal) => {
  const real = await importOriginal<typeof import("./utils.js")>();
  return { ...real, callApi: vi.fn() };
});

import { SandboxesNamespace } from "./Sandboxes.js";
import { callApi } from "./utils.js";
import type { Client as ApiClient } from "./api-clients/api/client/index.js";

// ─── Helpers ──────────────────────────────────────────────────────────────────

const mockCallApi = vi.mocked(callApi);

function makeApiClient(): ApiClient {
  return {} as ApiClient;
}

function makeRawSandbox(overrides: Record<string, unknown> = {}) {
  return {
    id: "abc123",
    status: "running",
    agent_url: "https://agent.example.com",
    agent_token: "tok-xyz",
    project_id: "proj-1",
    ephemeral: false,
    current_version_number: 1,
    next_version_number: 2,
    millicpu: 1000,
    gpu: null,
    memory_bytes: 2147483648,
    disk_bytes: 10737418240,
    version_count: 1,
    agent_version: "1.0.0",
    agent_type: "default",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
    ...overrides,
  };
}

// ─── SandboxesNamespace.create ────────────────────────────────────────────────

describe("SandboxesNamespace.create", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends autostart: true to the create API", async () => {
    const createdRaw = makeRawSandbox({ id: "abc123", status: "starting" });
    const runningRaw = makeRawSandbox({ id: "abc123", status: "running" });

    // First callApi call → createSandbox, second → waitForSandbox
    mockCallApi
      .mockResolvedValueOnce(createdRaw)
      .mockResolvedValueOnce(runningRaw);

    const ns = new SandboxesNamespace(makeApiClient());
    await ns.create({ snapshotId: "snap-1" });

    expect(mockCallApi.mock.calls[0][0]).toBe("api.createSandbox");
  });

  it("calls waitForSandbox with the ID from createSandbox", async () => {
    const createdRaw = makeRawSandbox({ id: "new-id", status: "starting" });
    const runningRaw = makeRawSandbox({ id: "new-id", status: "running" });

    mockCallApi
      .mockResolvedValueOnce(createdRaw)
      .mockResolvedValueOnce(runningRaw);

    const ns = new SandboxesNamespace(makeApiClient());
    await ns.create({ snapshotAlias: "my-snap" });

    expect(mockCallApi).toHaveBeenCalledTimes(2);
    expect(mockCallApi.mock.calls[0][0]).toBe("api.createSandbox");
    expect(mockCallApi.mock.calls[1][0]).toBe("api.waitForSandbox");
  });

  it("returns a Sandbox with the id from the running sandbox", async () => {
    const createdRaw = makeRawSandbox({ id: "abc123", status: "starting" });
    const runningRaw = makeRawSandbox({ id: "abc123", status: "running" });

    mockCallApi
      .mockResolvedValueOnce(createdRaw)
      .mockResolvedValueOnce(runningRaw);

    const ns = new SandboxesNamespace(makeApiClient());
    const sandbox = await ns.create();

    expect(sandbox.id).toBe("abc123");
  });

  it("throws if waitForSandbox resolves to a non-running status", async () => {
    const createdRaw = makeRawSandbox({ id: "abc123", status: "starting" });
    const failedRaw = makeRawSandbox({ id: "abc123", status: "start_failed" });

    mockCallApi
      .mockResolvedValueOnce(createdRaw)
      .mockResolvedValueOnce(failedRaw);

    const ns = new SandboxesNamespace(makeApiClient());
    await expect(ns.create()).rejects.toThrow();
  });
});

import { describe, it, expect, vi, beforeEach } from "vitest";
import * as apiModule from "./api-clients/api/index.js";
import { SandboxesNamespace } from "./Sandboxes.js";
import type { Client as ApiClient } from "./api-clients/api/client/index.js";

// ─── Helpers ──────────────────────────────────────────────────────────────────

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
    vi.restoreAllMocks();
  });

  it("calls createSandbox with autostart: true", async () => {
    const createdRaw = makeRawSandbox({ status: "starting" });
    const runningRaw = makeRawSandbox({ status: "running" });

    const createSpy = vi
      .spyOn(apiModule, "createSandbox")
      .mockResolvedValue({ data: createdRaw, response: new Response() } as never);
    vi.spyOn(apiModule, "waitForSandbox").mockResolvedValue({
      data: runningRaw,
      response: new Response(),
    } as never);

    const ns = new SandboxesNamespace(makeApiClient());
    await ns.create({ snapshotId: "snap-1" });

    expect(createSpy).toHaveBeenCalledOnce();
    const body = createSpy.mock.calls[0][0].body as Record<string, unknown>;
    expect(body.autostart).toBe(true);
    expect(body.snapshot_id).toBe("snap-1");
  });

  it("waits for the sandbox using the ID returned by createSandbox", async () => {
    const createdRaw = makeRawSandbox({ id: "newly-created", status: "starting" });
    const runningRaw = makeRawSandbox({ id: "newly-created", status: "running" });

    vi.spyOn(apiModule, "createSandbox").mockResolvedValue({
      data: createdRaw,
      response: new Response(),
    } as never);
    const waitSpy = vi
      .spyOn(apiModule, "waitForSandbox")
      .mockResolvedValue({ data: runningRaw, response: new Response() } as never);

    const ns = new SandboxesNamespace(makeApiClient());
    await ns.create({ snapshotAlias: "my-snap" });

    expect(waitSpy).toHaveBeenCalledOnce();
    expect(waitSpy.mock.calls[0][0].path).toEqual({ id: "newly-created" });
  });

  it("returns a Sandbox with the id from waitForSandbox", async () => {
    const createdRaw = makeRawSandbox({ id: "abc123", status: "starting" });
    const runningRaw = makeRawSandbox({ id: "abc123", status: "running" });

    vi.spyOn(apiModule, "createSandbox").mockResolvedValue({
      data: createdRaw,
      response: new Response(),
    } as never);
    vi.spyOn(apiModule, "waitForSandbox").mockResolvedValue({
      data: runningRaw,
      response: new Response(),
    } as never);

    const ns = new SandboxesNamespace(makeApiClient());
    const sandbox = await ns.create();

    expect(sandbox.id).toBe("abc123");
  });

  it("throws if waitForSandbox resolves to a non-running status", async () => {
    const createdRaw = makeRawSandbox({ status: "starting" });
    const failedRaw = makeRawSandbox({ status: "start_failed" });

    vi.spyOn(apiModule, "createSandbox").mockResolvedValue({
      data: createdRaw,
      response: new Response(),
    } as never);
    vi.spyOn(apiModule, "waitForSandbox").mockResolvedValue({
      data: failedRaw,
      response: new Response(),
    } as never);

    const ns = new SandboxesNamespace(makeApiClient());
    await expect(ns.create()).rejects.toThrow();
  });
});

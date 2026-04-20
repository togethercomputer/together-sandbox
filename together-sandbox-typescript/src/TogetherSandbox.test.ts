import { describe, it, expect } from "vitest";
import { TogetherSandbox } from "./TogetherSandbox.js";
import { Sandbox } from "./Sandbox.js";
import type { Sandbox as SandboxModel } from "./api-clients/api/types.gen.js";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function makeVmInfo(overrides: Partial<SandboxModel> = {}): SandboxModel {
  return {
    _type: "sandbox",
    id: "test-sandbox-123",
    status: "running",
    ephemeral: false,
    cluster_name: "us-east-1",
    current_version_number: 1,
    next_version_number: 2,
    millicpu: 2000,
    gpu: 0,
    memory_bytes: 2147483648,
    disk_bytes: 10737418240,
    version_count: 1,
    agent_version: "1.0.0",
    agent_type: "bartender",
    agent_token: "agent-tok",
    agent_url: "https://agent.example.com",
    created_at: "2026-04-13T00:00:00Z",
    start_scheduled_at: null,
    start_type: "cold_start",
    started_at: "2026-04-13T00:00:01Z",
    stop_scheduled_at: null,
    scheduled_stop_type: null,
    stopped_at: null,
    stop_reason: null,
    specs_updated_at: null,
    recovery_status: null,
    recovery_scheduled_at: null,
    recovery_finished_at: null,
    updated_at: "2026-04-13T00:00:01Z",
    ...overrides,
  };
}

// ─── Sandbox tests ───────────────────────────────────────────────────────────

describe("Sandbox", () => {
  it("id getter returns vmInfo.id", () => {
    const vmInfo = makeVmInfo({ id: "test-id-456" });
    const sandbox = new Sandbox(vmInfo, {} as any, {} as any);
    expect(sandbox.id).toBe("test-id-456");
  });

  it("exposes vmInfo", () => {
    const vmInfo = makeVmInfo();
    const sandbox = new Sandbox(vmInfo, {} as any, {} as any);
    expect(sandbox.vmInfo).toBe(vmInfo);
  });

  it("does not expose sandboxClient as public property", () => {
    const mockClient = {} as any;
    const sandbox = new Sandbox(makeVmInfo(), mockClient, {} as any);
    expect((sandbox as any).sandboxClient).toBeUndefined();
  });

  it("files namespace has expected methods including move, copy, watch", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const files = sandbox.files;
    expect(files).toHaveProperty("read");
    expect(files).toHaveProperty("create");
    expect(files).toHaveProperty("delete");
    expect(files).toHaveProperty("move");
    expect(files).toHaveProperty("copy");
    expect(files).toHaveProperty("stat");
    expect(files).toHaveProperty("watch");
    // action is removed (replaced by move/copy)
    expect(files).not.toHaveProperty("action");
  });

  it("directories namespace has expected methods", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const dirs = sandbox.directories;
    expect(dirs).toHaveProperty("list");
    expect(dirs).toHaveProperty("create");
    expect(dirs).toHaveProperty("delete");
  });

  it("execs namespace has renamed methods (streamOutput, sendStdin, streamList)", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const execs = sandbox.execs;
    expect(execs).toHaveProperty("list");
    expect(execs).toHaveProperty("create");
    expect(execs).toHaveProperty("get");
    expect(execs).toHaveProperty("update");
    expect(execs).toHaveProperty("delete");
    expect(execs).toHaveProperty("streamOutput");
    expect(execs).toHaveProperty("sendStdin");
    expect(execs).toHaveProperty("streamList");
    // Old names should not exist
    expect(execs).not.toHaveProperty("output");
    expect(execs).not.toHaveProperty("stdin");
    expect(execs).not.toHaveProperty("stream");
  });

  it("tasks namespace has expected methods", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const tasks = sandbox.tasks;
    expect(tasks).toHaveProperty("list");
    expect(tasks).toHaveProperty("get");
    expect(tasks).toHaveProperty("action");
    expect(tasks).toHaveProperty("listSetup");
  });

  it("ports namespace has streamList (renamed from stream)", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const ports = sandbox.ports;
    expect(ports).toHaveProperty("list");
    expect(ports).toHaveProperty("streamList");
    expect(ports).not.toHaveProperty("stream");
  });
});

// ─── TogetherSandbox tests ───────────────────────────────────────────────────

describe("TogetherSandbox", () => {
  it("exposes sandboxes", () => {
    const sdk = new TogetherSandbox({ apiKey: "test-key" });
    expect(sdk).toHaveProperty("sandboxes");
  });

  it("does not expose apiClient", () => {
    const sdk = new TogetherSandbox({ apiKey: "test-key" });
    expect((sdk as any).apiClient).toBeUndefined();
  });
});

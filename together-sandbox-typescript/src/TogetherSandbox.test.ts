import { describe, it, expect, vi } from "vitest";
import { TogetherSandbox } from "./TogetherSandbox.js";
import { Sandbox } from "./Sandbox.js";
import { camelCaseKeys, type SandboxInfo } from "./types.js";
import * as api from "./api-clients/api/index.js";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function makeVmInfo(overrides: Partial<SandboxInfo> = {}): SandboxInfo {
  return {
    _type: "sandbox",
    id: "test-sandbox-123",
    status: "running",
    ephemeral: false,
    clusterName: "us-east-1",
    currentVersionNumber: 1,
    nextVersionNumber: 2,
    millicpu: 2000,
    gpu: 0,
    memoryBytes: 2147483648,
    diskBytes: 10737418240,
    versionCount: 1,
    agentVersion: "1.0.0",
    agentType: "bartender",
    agentToken: "agent-tok",
    agentUrl: "https://agent.example.com",
    createdAt: "2026-04-13T00:00:00Z",
    startScheduledAt: null,
    startType: "cold_start",
    startedAt: "2026-04-13T00:00:01Z",
    stopScheduledAt: null,
    scheduledStopType: null,
    stoppedAt: null,
    stopReason: null,
    specsUpdatedAt: null,
    recoveryStatus: null,
    recoveryScheduledAt: null,
    recoveryFinishedAt: null,
    updatedAt: "2026-04-13T00:00:01Z",
    ...overrides,
  };
}

describe("camelCaseKeys", () => {
  it("converts snake_case keys to camelCase", () => {
    expect(
      camelCaseKeys({ cluster_name: "us-east-1", memory_bytes: 1024 }),
    ).toEqual({ clusterName: "us-east-1", memoryBytes: 1024 });
  });

  it("preserves leading underscores (_type)", () => {
    expect(camelCaseKeys({ _type: "sandbox", stop_reason: null })).toEqual({
      _type: "sandbox",
      stopReason: null,
    });
  });

  it("handles multi-segment keys (current_version_number)", () => {
    expect(camelCaseKeys({ current_version_number: 3 })).toEqual({
      currentVersionNumber: 3,
    });
  });
});

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

  describe("snapshots namespace", () => {
    it("has create method and old methods are removed", () => {
      const sdk = new TogetherSandbox({ apiKey: "test-key" });
      expect(sdk.snapshots).toHaveProperty("create");
      expect(sdk.snapshots).not.toHaveProperty("fromBuild");
      expect(sdk.snapshots).not.toHaveProperty("fromImage");
    });

    it("has get and getByAlias methods", () => {
      const sdk = new TogetherSandbox({ apiKey: "test-key" });
      expect(sdk.snapshots).toHaveProperty("getById");
      expect(sdk.snapshots).toHaveProperty("getByAlias");
      expect(sdk.snapshots).not.toHaveProperty("getSnapshot");
    });

    it("getByAlias strips leading @ from alias", async () => {
      const spy = vi.spyOn(api, "getSnapshotByAlias").mockResolvedValue({
        data: {
          id: "snap-1",
          _type: "snapshot",
          byte_size: 0,
          protected: false,
          optimized: false,
          includes_memory_snapshot: false,
          created_at: "",
          optimized_at: null,
          updated_at: "",
        },
      } as any);

      const sdk = new TogetherSandbox({ apiKey: "test-key" });
      await sdk.snapshots.getByAlias("@my-app@latest");

      expect(spy).toHaveBeenCalledWith(
        expect.objectContaining({ path: { alias: "my-app@latest" } }),
      );
      spy.mockRestore();
    });
  });
});

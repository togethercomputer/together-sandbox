import { describe, it, expect } from "vitest";
import { resolveConnectionDetails, Sandbox } from "./TogetherSandbox.js";
import type { VmStartResponseData } from "./api-clients/api/types.gen.js";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function makeVmInfo(overrides: Partial<VmStartResponseData> = {}): VmStartResponseData {
  return {
    bootup_type: "cold",
    cluster: "us-east-1",
    id: "test-sandbox-123",
    latest_pitcher_version: "1.0.0",
    pitcher_manager_version: "1.0.0",
    pitcher_token: "pitcher-tok",
    pitcher_url: "https://pitcher.example.com",
    pitcher_version: "1.0.0",
    reconnect_token: "reconnect-tok",
    use_pint: false,
    user_workspace_path: "/home/user/workspace",
    vm_agent_type: "pint",
    workspace_path: "/workspace",
    ...overrides,
  };
}

// ─── resolveConnectionDetails tests ──────────────────────────────────────────

describe("resolveConnectionDetails", () => {
  it("prefers pint when use_pint is true and pint fields present", () => {
    const vmInfo = makeVmInfo({
      use_pint: true,
      pint_url: "https://pint.example.com",
      pint_token: "pint-tok",
    });

    const { url, token } = resolveConnectionDetails(vmInfo);
    expect(url).toBe("https://pint.example.com");
    expect(token).toBe("pint-tok");
  });

  it("falls back to pitcher when use_pint is false", () => {
    const vmInfo = makeVmInfo({
      use_pint: false,
      pint_url: "https://pint.example.com",
      pint_token: "pint-tok",
    });

    const { url, token } = resolveConnectionDetails(vmInfo);
    expect(url).toBe("https://pitcher.example.com");
    expect(token).toBe("pitcher-tok");
  });

  it("falls back to pitcher when pint_url is undefined", () => {
    const vmInfo = makeVmInfo({
      use_pint: true,
      pint_url: undefined,
      pint_token: undefined,
    });

    const { url, token } = resolveConnectionDetails(vmInfo);
    expect(url).toBe("https://pitcher.example.com");
    expect(token).toBe("pitcher-tok");
  });

  it("falls back to pitcher when pint_token is undefined", () => {
    const vmInfo = makeVmInfo({
      use_pint: true,
      pint_url: "https://pint.example.com",
      pint_token: undefined,
    });

    const { url, token } = resolveConnectionDetails(vmInfo);
    expect(url).toBe("https://pitcher.example.com");
    expect(token).toBe("pitcher-tok");
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

  it("exposes sandboxClient", () => {
    const mockClient = {} as any;
    const sandbox = new Sandbox(makeVmInfo(), mockClient, {} as any);
    expect(sandbox.sandboxClient).toBe(mockClient);
  });

  it("files namespace has expected methods", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const files = sandbox.files;
    expect(files).toHaveProperty("read");
    expect(files).toHaveProperty("create");
    expect(files).toHaveProperty("delete");
    expect(files).toHaveProperty("action");
    expect(files).toHaveProperty("stat");
  });

  it("directories namespace has expected methods", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const dirs = sandbox.directories;
    expect(dirs).toHaveProperty("list");
    expect(dirs).toHaveProperty("create");
    expect(dirs).toHaveProperty("delete");
  });

  it("execs namespace has expected methods", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const execs = sandbox.execs;
    expect(execs).toHaveProperty("list");
    expect(execs).toHaveProperty("create");
    expect(execs).toHaveProperty("get");
    expect(execs).toHaveProperty("update");
    expect(execs).toHaveProperty("delete");
    expect(execs).toHaveProperty("output");
    expect(execs).toHaveProperty("stdin");
    expect(execs).toHaveProperty("stream");
  });

  it("tasks namespace has expected methods", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const tasks = sandbox.tasks;
    expect(tasks).toHaveProperty("list");
    expect(tasks).toHaveProperty("get");
    expect(tasks).toHaveProperty("action");
    expect(tasks).toHaveProperty("setup");
  });

  it("ports namespace has expected methods", () => {
    const sandbox = new Sandbox(makeVmInfo(), {} as any, {} as any);
    const ports = sandbox.ports;
    expect(ports).toHaveProperty("list");
    expect(ports).toHaveProperty("stream");
  });
});

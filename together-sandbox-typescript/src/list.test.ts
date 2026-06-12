import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "./api-clients/api/index.js";
import { SnapshotsNamespace } from "./Snapshots.js";
import { SandboxesNamespace } from "./Sandboxes.js";

vi.mock("./api-clients/api/index.js", async (importOriginal) => {
  const actual =
    await importOriginal<typeof import("./api-clients/api/index.js")>();
  return {
    ...actual,
    listSnapshots: vi.fn(),
    listSandboxes: vi.fn(),
    getSandbox: vi.fn(),
  };
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const fakeClient = {} as any;

describe("Snapshots.list", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns the page wrapper and forwards pagination params", async () => {
    const page = { data: [{ id: "snap_1" }], next_cursor: "next-token" };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSnapshots as any).mockResolvedValue({
      data: page,
      response: new Response(null, { status: 200 }),
    });

    const ns = new SnapshotsNamespace(fakeClient, "https://x", "key");
    const result = await ns.list({ limit: 5, cursor: "c", projectId: "p" });

    expect(result).toEqual(page);
    expect(result.next_cursor).toBe("next-token");
    expect(api.listSnapshots).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { project_id: "p", limit: 5, cursor: "c" },
      }),
    );
  });

  it("sends undefined query params when called with no args", async () => {
    const page = { data: [], next_cursor: null };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSnapshots as any).mockResolvedValue({
      data: page,
      response: new Response(null, { status: 200 }),
    });

    const ns = new SnapshotsNamespace(fakeClient, "https://x", "key");
    const result = await ns.list();

    expect(result).toEqual(page);
    expect(api.listSnapshots).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { project_id: undefined, limit: undefined, cursor: undefined },
      }),
    );
  });
});

describe("Sandboxes.list", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns the page wrapper and forwards pagination params", async () => {
    const page = { data: [{ id: "sb_1" }], next_cursor: null };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSandboxes as any).mockResolvedValue({
      data: page,
      response: new Response(null, { status: 200 }),
    });

    const ns = new SandboxesNamespace(fakeClient);
    const result = await ns.list({ limit: 10 });

    expect(result).toEqual(page);
    expect(result.next_cursor).toBeNull();
    expect(api.listSandboxes).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { project_id: undefined, limit: 10, cursor: undefined },
      }),
    );
  });
});

describe("Sandboxes.get", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns the record and forwards the id in the path", async () => {
    const record = { id: "sb_1", status: "running" };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.getSandbox as any).mockResolvedValue({
      data: record,
      response: new Response(null, { status: 200 }),
    });

    const ns = new SandboxesNamespace(fakeClient);
    const result = await ns.get("sb_1");

    expect(result).toEqual(record);
    expect(api.getSandbox).toHaveBeenCalledWith(
      expect.objectContaining({ path: { id: "sb_1" } }),
    );
  });
});

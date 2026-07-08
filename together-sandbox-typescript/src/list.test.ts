import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "./api-clients/api/index.js";
import { SnapshotsNamespace } from "./Snapshots.js";
import { SandboxesNamespace } from "./Sandboxes.js";
import { Page } from "./pagination.js";

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

  it("returns a Page and forwards pagination params", async () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSnapshots as any).mockResolvedValue({
      data: { data: [{ id: "snap_1" }], next_cursor: "next-token" },
      response: new Response(null, { status: 200 }),
    });

    const ns = new SnapshotsNamespace(fakeClient, "https://x", "key");
    const page = await ns.list({ limit: 5 });

    expect(page).toBeInstanceOf(Page);
    expect(page.data).toEqual([{ id: "snap_1" }]);
    expect(page.nextCursor).toBe("next-token");
    expect(page.hasNextPage()).toBe(true);
    expect(api.listSnapshots).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { limit: 5, cursor: undefined },
      }),
    );
  });

  it("forwards a starting cursor", async () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSnapshots as any).mockResolvedValue({
      data: { data: [], next_cursor: null },
      response: new Response(null, { status: 200 }),
    });

    const ns = new SnapshotsNamespace(fakeClient, "https://x", "key");
    await ns.list({ limit: 5, cursor: "page-2" });

    expect(api.listSnapshots).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { limit: 5, cursor: "page-2" },
      }),
    );
  });

  it("sends undefined query params when called with no args", async () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSnapshots as any).mockResolvedValue({
      data: { data: [], next_cursor: null },
      response: new Response(null, { status: 200 }),
    });

    const ns = new SnapshotsNamespace(fakeClient, "https://x", "key");
    const page = await ns.list();

    expect(page.data).toEqual([]);
    expect(page.hasNextPage()).toBe(false);
    expect(api.listSnapshots).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { limit: undefined, cursor: undefined },
      }),
    );
  });
});

describe("Sandboxes.list", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns a Page of camelCased records and forwards pagination params", async () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSandboxes as any).mockResolvedValue({
      data: { data: [{ id: "sb_1", cluster_name: "c1" }], next_cursor: null },
      response: new Response(null, { status: 200 }),
    });

    const ns = new SandboxesNamespace(fakeClient);
    const page = await ns.list({ limit: 10 });

    expect(page).toBeInstanceOf(Page);
    expect(page.data).toEqual([{ id: "sb_1", clusterName: "c1" }]);
    expect(page.nextCursor).toBeNull();
    expect(api.listSandboxes).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { project_id: undefined, limit: 10, cursor: undefined },
      }),
    );
  });

  it("forwards a starting cursor", async () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.listSandboxes as any).mockResolvedValue({
      data: { data: [], next_cursor: null },
      response: new Response(null, { status: 200 }),
    });

    const ns = new SandboxesNamespace(fakeClient);
    await ns.list({ limit: 10, cursor: "page-2" });

    expect(api.listSandboxes).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { project_id: undefined, limit: 10, cursor: "page-2" },
      }),
    );
  });
});

describe("Sandboxes.get", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns the camelCased record and forwards the id in the path", async () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.getSandbox as any).mockResolvedValue({
      data: { id: "sb_1", status: "running", agent_url: "https://agent" },
      response: new Response(null, { status: 200 }),
    });

    const ns = new SandboxesNamespace(fakeClient);
    const result = await ns.get("sb_1");

    expect(result).toEqual({
      id: "sb_1",
      status: "running",
      agentUrl: "https://agent",
    });
    expect(api.getSandbox).toHaveBeenCalledWith(
      expect.objectContaining({ path: { id: "sb_1" } }),
    );
  });
});

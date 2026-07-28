import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { RemoteImageBuilderClient } from "./RemoteImageBuilder.js";

/**
 * The builder POSTs a multipart form to the image-builder service, so these
 * assert the form fields — they are the actual contract with that service.
 * Log streaming needs a live build and is stubbed out.
 */
describe("RemoteImageBuilderClient.build", () => {
  let contextDir: string;
  let posts: FormData[];

  beforeEach(() => {
    contextDir = fs.mkdtempSync(path.join(os.tmpdir(), "ib-test-"));
    fs.writeFileSync(path.join(contextDir, "Dockerfile"), "FROM alpine\n");
    posts = [];

    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string, init: RequestInit) => {
        expect(url).toBe("https://ib.test/builds");
        expect(init.method).toBe("POST");
        posts.push(init.body as FormData);
        return new Response(JSON.stringify({ build_id: "b1" }), { status: 202 });
      }),
    );

    vi.spyOn(
      RemoteImageBuilderClient.prototype as unknown as {
        _streamUntilDone: (id: string) => Promise<string>;
      },
      "_streamUntilDone",
    ).mockResolvedValue("registry/ns/app:v1");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    fs.rmSync(contextDir, { recursive: true, force: true });
  });

  const build = async (opts: { cacheKey?: string } = {}) => {
    const client = new RemoteImageBuilderClient({
      apiUrl: "https://ib.test",
      token: "tok",
    });
    const ref = await client.build({
      contextDir,
      imageName: "app:v1",
      ...opts,
    });
    expect(ref).toBe("registry/ns/app:v1");
    expect(posts).toHaveLength(1);
    return posts[0]!;
  };

  it("sends cache_key when given", async () => {
    const form = await build({ cacheKey: "envs/python" });
    expect(form.get("cache_key")).toBe("envs/python");
  });

  it("omits cache_key when absent", async () => {
    const form = await build();
    // Absent rather than empty: the server defaults an omitted cache_key to
    // the image name without its tag.
    expect(form.has("cache_key")).toBe(false);
  });

  it("omits cache_key when empty", async () => {
    const form = await build({ cacheKey: "" });
    expect(form.has("cache_key")).toBe(false);
  });

  it("leaves the other fields unchanged", async () => {
    const form = await build({ cacheKey: "k" });
    expect(form.get("image_name")).toBe("app:v1");
    expect(form.get("dockerfile")).toBe("Dockerfile");
    expect(form.get("build_args")).toBe("{}");
    expect(form.get("nydus_convert")).toBe("true");
    expect(form.get("context")).toBeInstanceOf(Blob);
  });
});

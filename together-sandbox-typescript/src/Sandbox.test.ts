import { describe, it, expect, vi } from "vitest";

import { Sandbox } from "./Sandbox.js";
import { createClient } from "./api-clients/sandbox/client/index.js";
import type { Client as ApiClient } from "./api-clients/api/client/index.js";
import type { SandboxInfo } from "./types.js";

// ─── Helpers ──────────────────────────────────────────────────────────────────

const BINARY = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x00, 0xff, 0xfe]);

function makeSandbox(respond: (request: Request) => Response) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) =>
    respond(input as Request),
  );
  const client = createClient({
    baseUrl: "http://agent.test",
    fetch: fetchMock as unknown as typeof fetch,
  });
  const sandbox = new Sandbox(
    { id: "abc123" } as SandboxInfo,
    client,
    {} as ApiClient,
    { maxAttempts: 1 },
  );
  return { sandbox, fetchMock };
}

function lastRequest(fetchMock: ReturnType<typeof vi.fn>): Request {
  return fetchMock.mock.calls.at(-1)![0] as Request;
}

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

// ─── files.readRaw ────────────────────────────────────────────────────────────

describe("files.readRaw", () => {
  it("requests octet-stream from the read endpoint and returns the bytes", async () => {
    const { sandbox, fetchMock } = makeSandbox(
      () =>
        new Response(BINARY, {
          status: 200,
          headers: { "Content-Type": "application/octet-stream" },
        }),
    );

    const result = await sandbox.files.readRaw("/assets/logo.png");

    expect(result).toEqual(BINARY);
    const request = lastRequest(fetchMock);
    expect(request.method).toBe("GET");
    expect(new URL(request.url).pathname).toBe(
      "/api/v1/files/%2Fassets%2Flogo.png",
    );
    expect(request.headers.get("Accept")).toBe("application/octet-stream");
  });

  it("returns empty bytes for an empty file", async () => {
    const { sandbox } = makeSandbox(
      () =>
        new Response(new Uint8Array(), {
          status: 200,
          headers: {
            "Content-Type": "application/octet-stream",
            "Content-Length": "0",
          },
        }),
    );

    expect(await sandbox.files.readRaw("/empty.bin")).toEqual(new Uint8Array());
  });

  it.each([
    [Buffer.from(BINARY).toString("base64"), "base64", BINARY],
    ["Hello 世界", "utf-8", new TextEncoder().encode("Hello 世界")],
  ])(
    "decodes JSON from agents without content negotiation (%s, %s)",
    async (content, encoding, expected) => {
      const { sandbox } = makeSandbox(() =>
        jsonResponse(200, { path: "/file", content, encoding }),
      );

      expect(await sandbox.files.readRaw("/file")).toEqual(expected);
    },
  );

  it("throws HttpError on not found", async () => {
    const { sandbox } = makeSandbox(() =>
      jsonResponse(404, { code: 404, message: "File not found" }),
    );

    await expect(sandbox.files.readRaw("/missing.bin")).rejects.toMatchObject({
      status: 404,
      message: expect.stringContaining("File not found"),
    });
  });
});

// ─── files.read ───────────────────────────────────────────────────────────────

describe("files.read", () => {
  it("does not ask for octet-stream", async () => {
    const { sandbox, fetchMock } = makeSandbox(() =>
      jsonResponse(200, { path: "/file", content: "text", encoding: "utf-8" }),
    );

    expect(await sandbox.files.read("/file")).toBe("text");
    expect(lastRequest(fetchMock).headers.get("Accept") ?? "").not.toContain(
      "application/octet-stream",
    );
  });
});

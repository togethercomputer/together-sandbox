import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { mkdtempSync, writeFileSync } from "fs";
import { rm } from "fs/promises";
import { join } from "path";
import { tmpdir } from "os";
import { TogetherSandbox } from "./TogetherSandbox.js";

// ─── Setup ─────────────────────────────────────────────────────────────────

const apiKey = process.env.CSB_API_KEY;
const describeIfKey = apiKey ? describe : describe.skip;

describeIfKey("snapshots.create (context)", () => {
  let sdk: TogetherSandbox;
  let tmpDir: string;

  beforeAll(() => {
    sdk = new TogetherSandbox({ apiKey: apiKey! });
    tmpDir = mkdtempSync(join(tmpdir(), "e2e-snapshot-"));
    writeFileSync(join(tmpDir, "Dockerfile"), "FROM alpine:latest\n");
  });

  afterAll(async () => {
    if (tmpDir) {
      await rm(tmpDir, { recursive: true });
    }
  });

  it("should build and register a snapshot with alias", async () => {
    const result = await sdk.snapshots.create({
      context: tmpDir,
      alias: "e2e-build",
    });

    expect(result.snapshotId).toBeTruthy();
    expect(typeof result.snapshotId).toBe("string");
    expect(result.snapshotId.length).toBeGreaterThan(0);
    expect(result.alias).toBeTruthy();
    expect(result.alias).toContain("e2e-build");
  });
});

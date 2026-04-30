import { describe, it, expect, vi } from "vitest";
import { camelCaseKeys } from "../src/utils";

describe("camelCaseKeys", () => {
  it("converts snake_case keys to camelCase", () => {
    expect(
      camelCaseKeys({ cluster_name: "us-east-1", memory_bytes: 1024 }),
    ).toEqual({ clusterName: "us-east-1", memoryBytes: 1024 });
  });

  it("handles multi-segment keys (current_version_number)", () => {
    expect(camelCaseKeys({ current_version_number: 3 })).toEqual({
      currentVersionNumber: 3,
    });
  });
});

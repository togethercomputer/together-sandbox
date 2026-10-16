import { describe, it, expect, afterEach, vi } from "vitest";
import {
  getBuilderUrl,
  getInferredBaseUrl,
  isErofsEnabled,
  isNydusEnabled,
} from "./configuration.js";

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("getInferredBaseUrl", () => {
  it("defaults to the v2 API", () => {
    vi.stubEnv("TOGETHER_BASE_URL", "");
    expect(getInferredBaseUrl()).toBe("https://api.v2.us.codesandbox.io");
  });

  it("prefers TOGETHER_BASE_URL", () => {
    vi.stubEnv("TOGETHER_BASE_URL", "https://api.bartender.codesandbox.io");
    expect(getInferredBaseUrl()).toBe("https://api.bartender.codesandbox.io");
  });
});

describe("getBuilderUrl", () => {
  it.each([
    ["https://api.v2.us.codesandbox.io", "https://builder.codesandbox.io"],
    ["https://api.bartender.codesandbox.io", "https://builder.codesandbox.io"],
    ["https://api.codesandbox.dev", "https://builder.codesandbox.dev"],
    ["http://localhost:4000", "http://localhost:4000"],
  ])("%s -> %s", (api, builder) => {
    expect(getBuilderUrl(api)).toBe(builder);
  });
});

describe("image optimization by host", () => {
  it.each([
    ["https://api.v2.us.codesandbox.io", true, false],
    ["https://api.bartender-v2.codesandbox.stream", true, false],
    ["https://api.bartender.codesandbox.io", false, true],
    ["https://api.codesandbox.dev", false, false],
  ])("%s: erofs=%s nydus=%s", (api, erofs, nydus) => {
    vi.stubEnv("TOGETHER_EROFS_ENABLED", "");
    vi.stubEnv("TOGETHER_NYDUS_ENABLED", "");
    expect(isErofsEnabled(api)).toBe(erofs);
    expect(isNydusEnabled(api)).toBe(nydus);
  });
});

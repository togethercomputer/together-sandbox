// Client factories re-exported from generated code so consumers don't need
// to import from internal paths
export {
  createClient as createApiClient,
  createConfig as createApiConfig,
  type Client as ApiClient,
  type Config as ApiConfig,
} from "./api-clients/api/client/index.js";
export {
  createClient as createSandboxClient,
  createConfig as createSandboxConfig,
  type Client as SandboxApiClient,
  type Config as SandboxApiConfig,
} from "./api-clients/sandbox/client/index.js";

// Unified facade — recommended entry point
export { TogetherSandbox } from "./TogetherSandbox.js";
export type { TogetherSandboxConfig } from "./configuration.js";

// Public camelCase types and facade classes
export type { SandboxInfo, CreateSandboxParams } from "./types.js";
export { Sandbox } from "./Sandbox.js";
export type { StartOptions, WatchOptions } from "./Sandbox.js";

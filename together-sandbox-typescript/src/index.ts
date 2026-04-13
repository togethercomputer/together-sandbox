// Generated clients as named namespaces.
// Using namespaces avoids conflicts since both clients re-export the same
// @hey-api/client-fetch internals (createClient, createConfig, Options, etc.)
export * as api from "./api-clients/api/index.js";
export * as sandbox from "./api-clients/sandbox/index.js";

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
export {
  TogetherSandbox,
  Sandbox,
  SandboxesNamespace,
} from "./TogetherSandbox.js";
export type {
  TogetherSandboxConfig,
  StartOptions,
  WatchOptions,
} from "./TogetherSandbox.js";

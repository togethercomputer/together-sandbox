// API wrapper class
export { API } from "./API.js";
export type { APIOptions, StartVmOptions } from "./API.js";

// Generated clients — both accessible from one entry point as named namespaces.
// Using namespaces avoids conflicts since both clients re-export the same
// @hey-api/client-fetch internals (createClient, createConfig, Options, etc.)
export * as api from "./api-clients/api/index.js";
export * as sandbox from "./api-clients/sandbox/index.js";

// Utilities
export {
  getInferredApiKey,
  getInferredBaseUrl,
  getInferredApiHost,
  getInferredRegistryUrl,
  isLocalEnvironment,
  isBetaAllowed,
} from "./utils/constants.js";

export {
  createApiClient,
  retryWithDelay,
  handleResponse,
  getDefaultTemplateId,
} from "./utils/api.js";

export { sleep } from "./utils/sleep.js";
export { base32Encode } from "./utils/encoding.js";

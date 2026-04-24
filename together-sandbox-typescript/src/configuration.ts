/**
 * Configuration for the {@link TogetherSandbox} facade.
 */
export interface TogetherSandboxConfig {
  /** Together AI API key. */
  apiKey?: string;
  /** Base URL for the management API. Defaults to `https://api.codesandbox.io`. */
  baseUrl?: string;
}

export function getInferredApiKey() {
  return process.env?.TOGETHER_API_KEY || process.env?.CSB_API_KEY;
}

export function getInferredBaseUrl() {
  if (process.env.CSB_BASE_URL) {
    return process.env.CSB_BASE_URL;
  }

  return "https://api.bartender.codesandbox.stream";
}

export function isLocalEnvironment(apiBaseUrl: string): boolean {
  const url = new URL(apiBaseUrl);
  const apiHostName = url.hostname;

  return apiHostName === "api.codesandbox.dev";
}

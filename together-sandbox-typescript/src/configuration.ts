export function getInferredApiKey() {
  return process.env?.TOGETHER_API_KEY;
}

export function getInferredBaseUrl() {
  if (process.env.TOGETHER_BASE_URL) {
    return process.env.TOGETHER_BASE_URL;
  }

  return "https://api.bartender.codesandbox.stream";
}

export function isLocalEnvironment(apiBaseUrl: string): boolean {
  const url = new URL(apiBaseUrl);
  const apiHostName = url.hostname;

  return apiHostName === "api.codesandbox.dev";
}

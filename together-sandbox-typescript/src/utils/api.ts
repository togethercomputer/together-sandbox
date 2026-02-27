import type { Client, Config } from "../api-clients/api/client/index.js";
import { createClient, createConfig } from "../api-clients/api/client/index.js";
import { getInferredBaseUrl } from "./constants.js";

function generateTraceParent(): string {
  const version = "00";
  const traceId = Array.from({ length: 32 }, () =>
    Math.floor(Math.random() * 16).toString(16)
  ).join("");
  const spanId = Array.from({ length: 16 }, () =>
    Math.floor(Math.random() * 16).toString(16)
  ).join("");
  const traceFlags = "01";
  return `${version}-${traceId}-${spanId}-${traceFlags}`;
}

async function enhanceFetch(
  request: RequestInfo | URL,
  instrumentation?: (request: Request) => Promise<Response>
) {
  const headers = new Headers(
    request instanceof Request ? request.headers : undefined
  );

  headers.set("traceparent", generateTraceParent());

  return instrumentation
    ? instrumentation(new Request(request, { headers }))
    : fetch(new Request(request, { headers }));
}

export function createApiClient(
  apiKey: string,
  config: Config = {},
  instrumentation?: (request: Request) => Promise<Response>
): Client {
  return createClient(
    createConfig({
      baseUrl: config.baseUrl ?? getInferredBaseUrl(apiKey),
      fetch: (request) => enhanceFetch(request, instrumentation),
      ...config,
      headers: {
        ...config.headers,
        Authorization: `Bearer ${apiKey}`,
      },
    })
  );
}

export type HandledResponse<D, E> = {
  data?: { data?: D };
  error?: E;
  response: Response;
};

export function getDefaultTemplateId(apiClient: Client): string {
  if (apiClient.getConfig().baseUrl?.includes("codesandbox.stream")) {
    return "7ngcrf";
  }
  return "pcz35m";
}

export async function retryWithDelay<T>(
  callback: () => Promise<T>,
  retries: number = 3,
  delay: number = 500
): Promise<T> {
  let lastError: Error = new Error("Retry failed");

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await callback();
    } catch (error) {
      lastError = error as Error;
      if (attempt === retries) throw lastError;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

export function handleResponse<D, E>(
  result: Awaited<{ data?: { data?: D }; error?: E; response: Response }>,
  errorPrefix: string
): D {
  if (result.response.status === 429 && "error" in result) {
    const error = (result.error as { errors: string[] }).errors[0];
    throw new Error(`${errorPrefix}: Rate limit exceeded. ${error ?? ""}`);
  }

  if (result.response.status === 404) {
    throw new Error(errorPrefix + ": Not found");
  }

  if (result.response.status === 403) {
    throw new Error(errorPrefix + ": Unauthorized");
  }

  if (result.response.status === 502) {
    throw new Error(errorPrefix + ": Bad gateway");
  }

  if (result.response.status === 503) {
    throw new Error(
      errorPrefix +
        ": The sandbox is currently overloaded. Please review your logic to reduce the number of concurrent requests or try again in a moment."
    );
  }

  if ("error" in result) {
    const error = (result.error as { errors: string[] }).errors[0];
    throw new Error(errorPrefix + ": " + error);
  }

  if (!result.data || !result.data.data) {
    throw new Error(errorPrefix + ": No data returned");
  }

  return result.data.data;
}

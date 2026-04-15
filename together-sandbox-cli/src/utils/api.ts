import {
  createClient as createApiClient,
  createConfig,
  type Client,
} from "../api-clients/api/client";
import { getInferredBaseUrl } from "./constants.js";

function generateTraceParent(): string {
  const version = "00";
  const traceId = Array.from({ length: 32 }, () =>
    Math.floor(Math.random() * 16).toString(16),
  ).join("");
  const spanId = Array.from({ length: 16 }, () =>
    Math.floor(Math.random() * 16).toString(16),
  ).join("");
  const traceFlags = "01";
  return `${version}-${traceId}-${spanId}-${traceFlags}`;
}

async function enhanceFetch(
  request: RequestInfo | URL,
  instrumentation?: (request: Request) => Promise<Response>,
) {
  const headers = new Headers(
    request instanceof Request ? request.headers : undefined,
  );
  headers.set("traceparent", generateTraceParent());
  return instrumentation
    ? instrumentation(new Request(request, { headers }))
    : fetch(new Request(request, { headers }));
}

export function createClient(
  apiKey: string,
  instrumentation?: (request: Request) => Promise<Response>,
): Client {
  return createApiClient(
    createConfig({
      baseUrl: getInferredBaseUrl(apiKey),
      fetch: (request) => enhanceFetch(request, instrumentation),
      headers: { Authorization: `Bearer ${apiKey}` },
      throwOnError: true,
    }),
  );
}

export function getDefaultTemplateId(client: Client): string {
  if (client.getConfig().baseUrl?.includes("codesandbox.stream")) {
    return "7ngcrf";
  }
  return "pcz35m";
}

export async function retryWithDelay<T>(
  callback: () => Promise<T>,
  retries: number = 3,
  delay: number = 500,
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

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

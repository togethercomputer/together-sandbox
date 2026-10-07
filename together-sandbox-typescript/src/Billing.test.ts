import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock the generated api-client module before any other import so the module
// graph resolves without the actual generated files (which may not exist in CI).
vi.mock("./api-clients/api/index.js", () => ({ getBillingUsage: vi.fn() }));
vi.mock("./api-clients/api/client/index.js", () => ({}));

// Mock callApi so tests control what each API call returns without needing
// real HTTP clients. This mirrors the approach used in Sandboxes.test.ts.
vi.mock("./utils.js", async (importOriginal) => {
  const real = await importOriginal<typeof import("./utils.js")>();
  return { ...real, callApi: vi.fn() };
});

import { BillingNamespace } from "./Billing.js";
import { callApi } from "./utils.js";
import * as api from "./api-clients/api/index.js";
import type { Client as ApiClient } from "./api-clients/api/client/index.js";

const mockCallApi = vi.mocked(callApi);

function makeApiClient(): ApiClient {
  return {} as ApiClient;
}

function makeRawUsageWindow(overrides: Record<string, unknown> = {}) {
  return {
    date: "2026-06-15",
    start_time: "2026-06-15T00:00:00Z",
    end_time: "2026-06-16T00:00:00Z",
    line_items: [
      {
        product_name: "Token Based Inference (Per 1M Tokens)",
        quantity: "1250.5",
        unit_price: "0.20",
        cost: "250.10",
        pricing_dimensions: { token_type: "input" },
        attributes: { api_key_id: "key_example", project_id: "proj_example" },
      },
    ],
    ...overrides,
  };
}

function makeRawUsagePage(overrides: Record<string, unknown> = {}) {
  return {
    object: "billing.usage_report",
    organization_id: "org_example",
    billing_period: "2026-06",
    earliest_window_start: "2026-06-01T00:00:00Z",
    latest_window_end: "2026-07-01T00:00:00Z",
    currency: "USD",
    data: [makeRawUsageWindow()],
    has_more: false,
    next_page_token: null,
    ...overrides,
  };
}

describe("BillingNamespace.usage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Run the thunk callApi is given so the query reaching the generated
    // client can be inspected.
    mockCallApi.mockImplementation((_op, thunk) => (thunk as () => never)());
  });

  it("passes month, granularity, limit and cursor through to the query", async () => {
    vi.mocked(api.getBillingUsage).mockResolvedValue(
      makeRawUsagePage() as never,
    );

    const ns = new BillingNamespace(makeApiClient());
    await ns.usage({
      month: "2026-06",
      granularity: "hour",
      limit: 50,
      cursor: "cursor-1",
    });

    expect(vi.mocked(api.getBillingUsage).mock.calls[0][0]?.query).toEqual({
      month: "2026-06",
      granularity: "hour",
      page_size: 50,
      page_token: "cursor-1",
    });
  });

  it("leaves the query unset when no options are given", async () => {
    vi.mocked(api.getBillingUsage).mockResolvedValue(
      makeRawUsagePage() as never,
    );

    const ns = new BillingNamespace(makeApiClient());
    await ns.usage();

    const query = vi.mocked(api.getBillingUsage).mock.calls[0][0]?.query;
    expect(query).toEqual({
      month: undefined,
      granularity: undefined,
      page_size: undefined,
      page_token: undefined,
    });
  });

  it("camelCases windows and nested line items, preserving decimal strings", async () => {
    vi.mocked(api.getBillingUsage).mockResolvedValue(
      makeRawUsagePage() as never,
    );

    const ns = new BillingNamespace(makeApiClient());
    const page = await ns.usage();

    expect(page.data).toEqual([
      {
        date: "2026-06-15",
        startTime: "2026-06-15T00:00:00Z",
        endTime: "2026-06-16T00:00:00Z",
        lineItems: [
          {
            productName: "Token Based Inference (Per 1M Tokens)",
            quantity: "1250.5",
            unitPrice: "0.20",
            cost: "250.10",
            pricingDimensions: { token_type: "input" },
            attributes: { api_key_id: "key_example", project_id: "proj_example" },
          },
        ],
      },
    ]);
  });

  it("exposes next_page_token as the page's nextCursor", async () => {
    vi.mocked(api.getBillingUsage).mockResolvedValue(
      makeRawUsagePage({ has_more: true, next_page_token: "next-token" }) as never,
    );

    const ns = new BillingNamespace(makeApiClient());
    const page = await ns.usage();

    expect(page.hasNextPage()).toBe(true);
    expect(page.nextCursor).toBe("next-token");
  });

  it("fetches the next page using the previous page's cursor", async () => {
    vi.mocked(api.getBillingUsage)
      .mockResolvedValueOnce(
        makeRawUsagePage({ has_more: true, next_page_token: "next-token" }) as never,
      )
      .mockResolvedValueOnce(makeRawUsagePage({ has_more: false }) as never);

    const ns = new BillingNamespace(makeApiClient());
    const page = await ns.usage({ month: "2026-06" });
    await page.getNextPage();

    expect(vi.mocked(api.getBillingUsage).mock.calls[1][0]?.query).toMatchObject({
      page_token: "next-token",
    });
  });
});

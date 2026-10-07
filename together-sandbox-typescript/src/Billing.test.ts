import { describe, it, expect, vi, afterEach } from "vitest";
import { BillingNamespace } from "./Billing.js";
import { HttpError } from "./errors.js";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function makeRawLineItem(overrides: Record<string, unknown> = {}) {
  return {
    product_name: "Token Based Inference (Per 1M Tokens)",
    quantity: "1250.5",
    unit_price: "0.20",
    cost: "250.10",
    pricing_dimensions: { token_type: "input" },
    attributes: { api_key_id: "key_example", project_id: "proj_example" },
    ...overrides,
  };
}

function makeRawWindow(overrides: Record<string, unknown> = {}) {
  return {
    date: "2026-06-15",
    start_time: "2026-06-15T00:00:00Z",
    end_time: "2026-06-16T00:00:00Z",
    line_items: [makeRawLineItem()],
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
    data: [makeRawWindow()],
    next_cursor: null,
    ...overrides,
  };
}

function mockFetchJson(body: unknown, status = 200): ReturnType<typeof vi.fn> {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
    text: async () => JSON.stringify(body),
  });
}

// ─── BillingNamespace.usage ───────────────────────────────────────────────────

describe("BillingNamespace.usage", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("requests the billing base URL with month, granularity, limit and cursor", async () => {
    const fetchMock = mockFetchJson(makeRawUsagePage());
    global.fetch = fetchMock as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");
    await ns.usage({
      month: "2026-06",
      granularity: "hour",
      limit: 50,
      cursor: "cursor-1",
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe(
      "https://api.together.ai/v1/billing/usage?month=2026-06&granularity=hour&page_size=50&page_token=cursor-1",
    );
    expect(init.headers.Authorization).toBe("Bearer test-key");
  });

  it("omits query params when no options are given", async () => {
    const fetchMock = mockFetchJson(makeRawUsagePage());
    global.fetch = fetchMock as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");
    await ns.usage();

    const [url] = fetchMock.mock.calls[0];
    expect(url).toBe("https://api.together.ai/v1/billing/usage?");
  });

  it("camelCases windows and nested line items, preserving decimal strings", async () => {
    global.fetch = mockFetchJson(makeRawUsagePage()) as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");
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

  it("treats a null next_cursor as the last page", async () => {
    global.fetch = mockFetchJson(makeRawUsagePage()) as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");
    const page = await ns.usage();

    expect(page.hasNextPage()).toBe(false);
    expect(page.nextCursor).toBeNull();
  });

  it("treats a missing next_cursor as the last page", async () => {
    const { next_cursor: _omit, ...raw } = makeRawUsagePage();
    global.fetch = mockFetchJson(raw) as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");
    const page = await ns.usage();

    expect(page.hasNextPage()).toBe(false);
  });

  it("exposes next_cursor as the page's nextCursor", async () => {
    global.fetch = mockFetchJson(
      makeRawUsagePage({ next_cursor: "next-token" }),
    ) as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");
    const page = await ns.usage();

    expect(page.hasNextPage()).toBe(true);
    expect(page.nextCursor).toBe("next-token");
  });

  it("fetches the next page using the previous page's cursor", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () =>
          makeRawUsagePage({ next_cursor: "next-token" }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => makeRawUsagePage(),
      });
    global.fetch = fetchMock as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");
    const page = await ns.usage({ month: "2026-06" });
    await page.getNextPage();

    const [secondUrl] = fetchMock.mock.calls[1];
    expect(secondUrl).toContain("page_token=next-token");
  });

  it("throws HttpError with the status and server message on failure", async () => {
    global.fetch = mockFetchJson(
      { code: "NOT_FOUND", message: "Organization not found", errors: [] },
      404,
    ) as unknown as typeof fetch;

    const ns = new BillingNamespace("test-key", "https://api.together.ai");

    await expect(ns.usage()).rejects.toMatchObject({
      status: 404,
      code: "NOT_FOUND",
    });
    await expect(ns.usage()).rejects.toBeInstanceOf(HttpError);
  });
});

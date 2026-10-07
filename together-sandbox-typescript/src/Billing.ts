import { withRetry, RETRYABLE_STATUS_CODES } from "./utils.js";
import { HttpError } from "./errors.js";
import type { RetryConfig } from "./types.js";
import { Page } from "./pagination.js";

/**
 * @internal Used by the `together-sandbox` CLI, not attached to the public
 * {@link TogetherSandbox} facade. Billing usage lives on the Together AI
 * platform API (`api.together.ai`), not the Bartender sandbox management API
 * the rest of this SDK talks to — hence the separate base URL and
 * hand-rolled `fetch` client below, rather than routing through
 * `api-clients/api`.
 */
export const DEFAULT_BILLING_BASE_URL = "https://api.together.ai";

/** A single cost-annotated billing line item within a usage window. */
export interface UsageLineItem {
  /** Human-readable label for the billed product. Display-only and not stable. */
  productName: string;
  /** Total usage for the window in the product's native unit, as a decimal string. */
  quantity: string;
  /** Per-unit price in USD, as a decimal string. */
  unitPrice: string;
  /** Total cost for the line item in USD, as a decimal string. */
  cost: string;
  /** Rate-determining dimensions as string key-value pairs. Varies by product. */
  pricingDimensions: Record<string, string>;
  /** Resource identifiers for attribution. `apiKeyId`/`projectId` are present for all line items. */
  attributes: Record<string, string>;
}

/** A time window (day or hour) containing the billing line items incurred within it. */
export interface UsageWindow {
  /** The date of the time window, YYYY-MM-DD. */
  date: string;
  /** Start of the time window (UTC, ISO 8601). */
  startTime: string;
  /** Exclusive end of the time window (UTC, ISO 8601). */
  endTime: string;
  lineItems: UsageLineItem[];
}

interface RawUsageLineItem {
  product_name: string;
  quantity: string;
  unit_price: string;
  cost: string;
  pricing_dimensions: Record<string, string>;
  attributes: Record<string, string>;
}

interface RawUsageWindow {
  date: string;
  start_time: string;
  end_time: string;
  line_items: RawUsageLineItem[];
}

interface RawUsagePage {
  object: "billing.usage_report";
  organization_id: string;
  billing_period: string;
  earliest_window_start: string | null;
  latest_window_end: string | null;
  currency: "USD";
  data: RawUsageWindow[];
  has_more: boolean;
  next_page_token: string | null;
}

function toUsageWindow(window: RawUsageWindow): UsageWindow {
  return {
    date: window.date,
    startTime: window.start_time,
    endTime: window.end_time,
    lineItems: window.line_items.map((item) => ({
      productName: item.product_name,
      quantity: item.quantity,
      unitPrice: item.unit_price,
      cost: item.cost,
      pricingDimensions: item.pricing_dimensions,
      attributes: item.attributes,
    })),
  };
}

/**
 * Billing usage operations, accessed as `sdk.billing.*`.
 *
 * Talks directly to the Together AI platform API — see
 * {@link DEFAULT_BILLING_BASE_URL}.
 */
export class BillingNamespace {
  constructor(
    private readonly _apiKey: string,
    private readonly _baseUrl: string,
    private readonly _retryConfig?: RetryConfig,
  ) {}

  /**
   * Get the authenticated organization's billing usage for a single month,
   * as cost-annotated line items grouped into time windows.
   *
   * Private beta: the organization behind the API key must be provisioned
   * for access, or this returns a 404.
   *
   * Returns a {@link Page} that is async-iterable across all pages of time
   * windows — iterate it directly to walk every window, or use
   * `getNextPage()` / `nextCursor` for manual page-by-page control.
   *
   * Usage data is cached: prior months refresh roughly every 24 hours, and
   * the current month refreshes roughly hourly.
   *
   * @param options.month Billing month as `YYYY-MM`. Defaults to the current
   *   month. Cannot be a future month or more than 12 months in the past.
   * @param options.granularity Time window size: `day` (default) or `hour`.
   * @param options.limit Max time windows per page (1-1000, default 100).
   * @param options.cursor Resume from a cursor returned by a previous page's
   *   {@link Page.nextCursor} (omit to start from the first page). Only
   *   valid for the `month` and `granularity` that produced it.
   */
  async usage(options?: {
    month?: string;
    granularity?: "day" | "hour";
    limit?: number;
    cursor?: string;
  }): Promise<Page<UsageWindow>> {
    const fetchPage = async (cursor?: string): Promise<Page<UsageWindow>> => {
      const query = new URLSearchParams();
      if (options?.month !== undefined) query.set("month", options.month);
      if (options?.granularity !== undefined)
        query.set("granularity", options.granularity);
      if (options?.limit !== undefined)
        query.set("page_size", String(options.limit));
      if (cursor !== undefined) query.set("page_token", cursor);

      const result = await withRetry<RawUsagePage>(
        "billing.getUsage",
        async () => {
          let response: Response;
          try {
            response = await fetch(
              `${this._baseUrl}/v1/billing/usage?${query.toString()}`,
              { headers: { Authorization: `Bearer ${this._apiKey}` } },
            );
          } catch (err) {
            // Transport-level failure (network, DNS, TLS, timeout) — surface
            // as `HttpError` with `status: 0`, matching `callApi`'s contract,
            // so `isRetryable` below treats it as retryable.
            const message = err instanceof Error ? err.message : String(err);
            throw new HttpError(`billing.getUsage: ${message}`, 0, {
              body: err,
              cause: err,
            });
          }
          if (!response.ok) {
            const body = await response.text().catch(() => "");
            let parsed: unknown;
            try {
              parsed = body ? JSON.parse(body) : undefined;
            } catch {
              parsed = undefined;
            }
            const errRecord =
              typeof parsed === "object" && parsed !== null
                ? (parsed as Record<string, unknown>)
                : undefined;
            const message =
              typeof errRecord?.message === "string"
                ? errRecord.message
                : body || `HTTP ${response.status}`;
            const code =
              typeof errRecord?.code === "string" ? errRecord.code : undefined;
            throw new HttpError(
              `Failed to billing.getUsage: ${message}${code ? ` (code: ${code})` : ""}`,
              response.status,
              { code, body: parsed ?? body },
            );
          }
          return (await response.json()) as RawUsagePage;
        },
        this._retryConfig,
        {
          isRetryable: (err) => {
            const status = (err as { status?: unknown })?.status;
            if (typeof status !== "number") return false;
            return status === 0 || RETRYABLE_STATUS_CODES.has(status);
          },
        },
      );

      return new Page<UsageWindow>(
        result.data.map(toUsageWindow),
        result.next_page_token,
        fetchPage,
      );
    };

    return fetchPage(options?.cursor);
  }
}

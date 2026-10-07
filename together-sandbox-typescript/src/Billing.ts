import * as api from "./api-clients/api/index.js";
import { type Client as ApiClient } from "./api-clients/api/client/index.js";
import type {
  BillingUsageLineItem as RawBillingUsageLineItem,
  BillingUsageWindow as RawBillingUsageWindow,
} from "./api-clients/api/types.gen.js";
import type { CamelCasedProperties, RetryConfig } from "./types.js";
import { camelCaseKeys, callApi } from "./utils.js";
import { Page } from "./pagination.js";

/**
 * A single cost-annotated billing line item within a usage window.
 *
 * `quantity`, `unitPrice`, and `cost` are decimal strings (not numbers) to
 * avoid floating-point precision loss on monetary values.
 */
export type UsageLineItem = CamelCasedProperties<RawBillingUsageLineItem>;

/**
 * A time window (day or hour, depending on the requested granularity)
 * containing the billing line items incurred within it.
 */
export type UsageWindow = Omit<
  CamelCasedProperties<RawBillingUsageWindow>,
  "lineItems"
> & {
  lineItems: UsageLineItem[];
};

function toUsageWindow(window: RawBillingUsageWindow): UsageWindow {
  return {
    ...camelCaseKeys(window),
    lineItems: window.line_items.map((item) => camelCaseKeys(item)),
  };
}

/**
 * Billing usage operations, accessed as `sdk.billing.*`.
 */
export class BillingNamespace {
  constructor(
    private readonly _apiClient: ApiClient,
    private readonly _retryConfig?: RetryConfig,
  ) {}

  /**
   * Get the authenticated organization's billing usage for a single month,
   * as cost-annotated line items grouped into time windows.
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
   * @param options.limit Max time windows per page (1–1000, default 100).
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
      const result = await callApi(
        "api.getBillingUsage",
        () =>
          api.getBillingUsage({
            client: this._apiClient,
            query: {
              month: options?.month,
              granularity: options?.granularity,
              page_size: options?.limit,
              page_token: cursor,
            },
          }),
        this._retryConfig,
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

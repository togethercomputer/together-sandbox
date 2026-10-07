import type * as yargs from "yargs";
import {
  BillingNamespace,
  DEFAULT_BILLING_BASE_URL,
  getInferredApiKey,
  Page,
  type UsageLineItem,
  type UsageWindow,
} from "together-sandbox";
import { runList, type ListArgs } from "./_list";
import { cell } from "./_table";
import { examples } from "./_help";

/**
 * This CLI is scoped to sandbox usage: only line items whose product name
 * contains "sandbox" (case-insensitive) are shown. `product_name` is
 * documented as display-only and not a stable identifier, but it's the only
 * signal the API exposes to tell sandbox compute apart from other Together
 * AI products (inference, dedicated endpoints, etc.) in the same report.
 * Windows left with no matching line items are dropped.
 */
function isSandboxProduct(item: UsageLineItem): boolean {
  return item.productName.toLowerCase().includes("sandbox");
}

function filterToSandboxProducts(windows: UsageWindow[]): UsageWindow[] {
  return windows
    .map((window) => ({
      ...window,
      lineItems: window.lineItems.filter(isSandboxProduct),
    }))
    .filter((window) => window.lineItems.length > 0);
}

/**
 * Wrap `billing.usage` so every page — including ones reached via
 * `getNextPage()` / async iteration — is pre-filtered to sandbox products
 * before `runList` or the interactive pager ever sees it.
 */
function fetchSandboxUsagePage(
  billing: BillingNamespace,
  options: { month?: string; granularity?: "day" | "hour" },
  params: { limit?: number; cursor?: string },
): Promise<Page<UsageWindow>> {
  const fetch = async (cursor?: string): Promise<Page<UsageWindow>> => {
    const page = await billing.usage({ ...options, ...params, cursor });
    return new Page(filterToSandboxProducts(page.data), page.nextCursor, fetch);
  };
  return fetch(params.cursor);
}

/**
 * Billing usage lives on the Together AI platform API, not the sandbox
 * management API — so it isn't part of `TogetherSandbox`. Build the
 * namespace directly from the same env-derived API key the rest of the CLI
 * uses.
 */
function createBillingNamespace(): BillingNamespace {
  const apiKey = getInferredApiKey();
  if (!apiKey) {
    throw new Error(
      "apiKey must be provided or TOGETHER_API_KEY env var must be set",
    );
  }
  return new BillingNamespace(apiKey, DEFAULT_BILLING_BASE_URL);
}

/** Sum of `cost` across a window's line items, formatted to 2 decimal places. */
function totalCost(window: UsageWindow): string {
  const total = window.lineItems.reduce(
    (sum, item) => sum + Number(item.cost),
    0,
  );
  return total.toFixed(2);
}

/** Distinct product names in a window, joined for a compact table cell. */
function products(window: UsageWindow): string {
  const names = [...new Set(window.lineItems.map((item) => item.productName))];
  return names.join(", ");
}

/** One billing line item with its window's time range inlined, for JSON output. */
interface UsageLineItemRecord extends UsageLineItem {
  date: string;
  startTime: string;
  endTime: string;
}

/**
 * Flatten windows into one record per line item. `-o json` emits these
 * instead of the nested `UsageWindow[]` so each element of `data` is a
 * self-contained, filterable record — e.g.
 * `together-sandbox billing usage -o json | jq '.data[] | select(.attributes.project_id == "...")'`.
 */
function toLineItemRecords(windows: UsageWindow[]): UsageLineItemRecord[] {
  return windows.flatMap((window) =>
    window.lineItems.map((item) => ({
      date: window.date,
      startTime: window.startTime,
      endTime: window.endTime,
      ...item,
    })),
  );
}

interface BillingUsageArgs extends ListArgs {
  month?: string;
  granularity?: string;
}

export const usageCommand: yargs.CommandModule<
  Record<string, never>,
  BillingUsageArgs
> = {
  command: "usage",
  describe:
    "Show sandbox billing usage for a month, as cost-annotated line items.",
  builder: (yargs) =>
    yargs
      .option("month", {
        type: "string",
        describe:
          "Billing month as YYYY-MM (default: current month; up to 12 months back)",
      })
      .option("granularity", {
        type: "string",
        choices: ["day", "hour"] as const,
        default: "day",
        describe: "Time window size; hour returns roughly 24x more rows",
      })
      .option("limit", {
        type: "number",
        describe: "Maximum number of time windows per page (1–1000)",
      })
      .option("cursor", {
        type: "string",
        describe:
          "Resume from a cursor (from a prior page); shows a single page and " +
          "disables the interactive pager",
      })
      .option("output", {
        alias: "o",
        type: "string",
        choices: ["table", "json"] as const,
        default: "table",
        describe: "Output format",
      })
      .option("ci", {
        type: "boolean",
        default: false,
        describe: "Plain output, no interactive pager",
      })
      .epilogue(
        examples([
          {
            describe: "Current month, by day",
            command: "$0 billing usage",
          },
          {
            describe: "A specific month, by hour",
            command: "$0 billing usage --month 2026-06 --granularity hour",
          },
          {
            describe:
              "Fetch one specific page (the next cursor is printed on stderr)",
            command: "$0 billing usage --limit 50 --cursor <cursor>",
          },
          {
            describe:
              "Machine-readable single page: { data, nextCursor }, one flat " +
              "line item per element of data",
            command: "$0 billing usage --ci -o json",
          },
          {
            describe: "Filter line items by project with jq",
            command:
              '$0 billing usage --ci -o json | jq \'.data[] | select(.attributes.project_id == "proj_example")\'',
          },
        ]),
      ) as unknown as yargs.Argv<BillingUsageArgs>,

  handler: async (argv) => {
    try {
      const billing = createBillingNamespace();
      await runList<UsageWindow, UsageLineItemRecord>(
        {
          fetchPage: (params) =>
            fetchSandboxUsagePage(
              billing,
              {
                month: argv.month,
                granularity: argv.granularity as "day" | "hour" | undefined,
              },
              params,
            ),
          headers: ["DATE", "PRODUCTS", "LINE ITEMS", "COST (USD)"],
          toRow: (window) => [
            cell(window.date),
            cell(products(window)),
            cell(window.lineItems.length),
            cell(totalCost(window)),
          ],
          toJson: toLineItemRecords,
        },
        argv,
      );
      process.exit(0);
    } catch (error) {
      console.error(
        error instanceof Error
          ? error.message
          : `Unknown error: ${JSON.stringify(error)}`,
      );
      process.exit(1);
    }
  },
};

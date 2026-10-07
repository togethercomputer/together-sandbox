import type * as yargs from "yargs";
import {
  BillingNamespace,
  DEFAULT_BILLING_BASE_URL,
  getInferredApiKey,
  type UsageLineItem,
} from "together-sandbox";
import { cell, renderTable } from "./_table";
import { examples } from "./_help";

/**
 * This CLI is scoped to sandbox usage: only line items whose product name
 * contains "sandbox" (case-insensitive) are shown. `product_name` is
 * documented as display-only and not a stable identifier, but it's the only
 * signal the API exposes to tell sandbox compute apart from other Together
 * AI products (inference, dedicated endpoints, etc.) in the same report.
 */
function isSandboxProduct(item: UsageLineItem): boolean {
  return item.productName.toLowerCase().includes("sandbox");
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

/** One billing line item with its window's time range inlined, for JSON output. */
interface UsageLineItemRecord extends UsageLineItem {
  date: string;
  startTime: string;
  endTime: string;
}

/**
 * A date's aggregated sandbox usage: every window on that date is merged, and
 * line items sharing the same product + pricing dimensions + attributes are
 * summed into one, so an hourly report doesn't show the same product once
 * per hour.
 */
interface DailyUsage {
  date: string;
  lineItems: UsageLineItemRecord[];
}

/** Stable key for "the same line item" across windows, for summing. */
function lineItemKey(item: UsageLineItem): string {
  return JSON.stringify([
    item.productName,
    item.pricingDimensions,
    item.attributes,
  ]);
}

/**
 * Add two decimal strings exactly, avoiding the float drift `Number(a) +
 * Number(b)` would introduce on money values (e.g. costs, quantities).
 * Scales both to the larger operand's decimal places and adds as integers.
 */
function addDecimalStrings(a: string, b: string): string {
  const decimalsOf = (s: string) => s.split(".")[1]?.length ?? 0;
  const scale = Math.max(decimalsOf(a), decimalsOf(b));
  const toScaledInt = (s: string) => Math.round(Number(s) * 10 ** scale);
  const sum = toScaledInt(a) + toScaledInt(b);
  return (sum / 10 ** scale).toFixed(scale);
}

/**
 * Walk every page of `billing.usage`, keep only sandbox line items, and
 * aggregate them by date — merging same-day windows (relevant at `hour`
 * granularity) and summing line items that share a product + pricing
 * dimensions + attributes, rather than listing one row per window.
 */
async function fetchDailySandboxUsage(
  billing: BillingNamespace,
  options: { month?: string; granularity?: "day" | "hour" },
): Promise<DailyUsage[]> {
  const byDate = new Map<string, Map<string, UsageLineItemRecord>>();

  const firstPage = await billing.usage(options);
  for await (const window of firstPage) {
    let byKey = byDate.get(window.date);
    if (!byKey) {
      byKey = new Map();
      byDate.set(window.date, byKey);
    }
    for (const item of window.lineItems) {
      if (!isSandboxProduct(item)) continue;
      const key = lineItemKey(item);
      const existing = byKey.get(key);
      if (existing) {
        existing.quantity = addDecimalStrings(existing.quantity, item.quantity);
        existing.cost = addDecimalStrings(existing.cost, item.cost);
        // Keep the earliest start / latest end across merged windows.
        if (window.startTime < existing.startTime) existing.startTime = window.startTime;
        if (window.endTime > existing.endTime) existing.endTime = window.endTime;
      } else {
        byKey.set(key, {
          ...item,
          date: window.date,
          startTime: window.startTime,
          endTime: window.endTime,
        });
      }
    }
  }

  return [...byDate.entries()]
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([date, byKey]) => ({ date, lineItems: [...byKey.values()] }))
    .filter((day) => day.lineItems.length > 0);
}

/** Sum of `cost` across a day's line items. */
function totalCost(day: DailyUsage): string {
  return day.lineItems.reduce((sum, item) => addDecimalStrings(sum, item.cost), "0");
}

/** Distinct product names on a day, joined for a compact table cell. */
function products(day: DailyUsage): string {
  const names = [...new Set(day.lineItems.map((item) => item.productName))];
  return names.join(", ");
}

interface BillingUsageArgs {
  month?: string;
  granularity?: string;
  output?: string;
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
        describe:
          "Time window size fetched from the API; results are always " +
          "aggregated by date regardless of granularity",
      })
      .option("output", {
        alias: "o",
        type: "string",
        choices: ["table", "json"] as const,
        default: "table",
        describe: "Output format",
      })
      .epilogue(
        examples([
          {
            describe: "Current month, aggregated by date",
            command: "$0 billing usage",
          },
          {
            describe: "A specific month",
            command: "$0 billing usage --month 2026-06",
          },
          {
            describe:
              "Machine-readable output: one flat line item per element of data",
            command: "$0 billing usage -o json",
          },
          {
            describe: "Filter line items by project with jq",
            command:
              '$0 billing usage -o json | jq \'.data[] | select(.attributes.project_id == "proj_example")\'',
          },
        ]),
      ) as unknown as yargs.Argv<BillingUsageArgs>,

  handler: async (argv) => {
    try {
      const billing = createBillingNamespace();
      const days = await fetchDailySandboxUsage(billing, {
        month: argv.month,
        granularity: argv.granularity as "day" | "hour" | undefined,
      });

      if (argv.output === "json") {
        const data = days.flatMap((day) => day.lineItems);
        process.stdout.write(`${JSON.stringify({ data }, null, 2)}\n`);
      } else {
        const rows = days.map((day) => [
          cell(day.date),
          cell(products(day)),
          cell(day.lineItems.length),
          cell(totalCost(day)),
        ]);
        process.stdout.write(
          `${renderTable(["DATE", "PRODUCTS", "LINE ITEMS", "COST (USD)"], rows, process.stdout.isTTY ? process.stdout.columns : undefined)}\n`,
        );
      }
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

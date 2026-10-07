import type * as yargs from "yargs";
import { TogetherSandbox } from "together-sandbox";
import type { UsageWindow } from "together-sandbox";
import { runList, type ListArgs } from "./_list";
import { cell } from "./_table";
import { examples } from "./_help";

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

interface BillingUsageArgs extends ListArgs {
  month?: string;
  granularity?: string;
}

export const usageCommand: yargs.CommandModule<
  Record<string, never>,
  BillingUsageArgs
> = {
  command: "usage",
  describe: "Show billing usage for a month, as cost-annotated line items.",
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
            describe: "Machine-readable single page: { data, nextCursor }",
            command: "$0 billing usage --ci -o json",
          },
        ]),
      ) as unknown as yargs.Argv<BillingUsageArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    try {
      await runList<UsageWindow>(
        {
          fetchPage: (params) =>
            sdk.billing.usage({
              ...params,
              month: argv.month,
              granularity: argv.granularity as "day" | "hour" | undefined,
            }),
          headers: ["DATE", "PRODUCTS", "LINE ITEMS", "COST (USD)"],
          toRow: (window) => [
            cell(window.date),
            cell(products(window)),
            cell(window.lineItems.length),
            cell(totalCost(window)),
          ],
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

import type * as yargs from "yargs";
import ora from "ora";
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

/** A date's total sandbox cost (CPU + Memory combined). */
interface DailyUsage {
  date: string;
  startTime: string;
  endTime: string;
  /** Total cost in USD, rounded to 2 decimal places, as a decimal string. */
  cost: string;
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
 * Round a USD decimal string to cents. Sum exactly first (see
 * {@link addDecimalStrings}) and round only the final total, so per-item
 * rounding errors don't accumulate. `Number.EPSILON` nudges half-cent values
 * like "1.005" (stored as 1.00499...) to round up as expected.
 */
function roundUsd(value: string): string {
  return (Math.round((Number(value) + Number.EPSILON) * 100) / 100).toFixed(2);
}

/**
 * Max days in a month. With `day` granularity a whole billing month fits in
 * one page of at most this many windows, so the CLI never needs to paginate.
 */
const MAX_DAYS_PER_MONTH = 31;

/**
 * Fetch a month of daily usage in a single page and sum the cost of each
 * date's sandbox line items into one total per day.
 */
async function fetchDailySandboxUsage(
  billing: BillingNamespace,
  options: { month?: string },
): Promise<DailyUsage[]> {
  const page = await billing.usage({
    ...options,
    granularity: "day",
    limit: MAX_DAYS_PER_MONTH,
  });
  return page.data
    .map((window) => ({
      date: window.date,
      startTime: window.startTime,
      endTime: window.endTime,
      cost: roundUsd(
        window.lineItems
          .filter(isSandboxProduct)
          .reduce((sum, item) => addDecimalStrings(sum, item.cost), "0"),
      ),
    }))
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
}

interface BillingUsageArgs {
  month?: string;
  output?: string;
}

export const usageCommand: yargs.CommandModule<
  Record<string, never>,
  BillingUsageArgs
> = {
  command: "usage",
  describe: "Show daily sandbox (CPU + Memory) billing cost for a month.",
  builder: (yargs) =>
    yargs
      .option("month", {
        type: "string",
        describe:
          "Billing month as YYYY-MM (default: current month; up to 12 months back)",
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
            describe: "Current month, one row per day",
            command: "$0 billing usage",
          },
          {
            describe: "A specific month",
            command: "$0 billing usage --month 2026-06",
          },
          {
            describe: "Machine-readable output",
            command: "$0 billing usage -o json",
          },
        ]),
      ) as unknown as yargs.Argv<BillingUsageArgs>,

  handler: async (argv) => {
    // Spinner goes to stderr so stdout stays clean for piping (e.g. `-o json | jq`).
    const spinner = ora({
      text: "Fetching billing usage...",
      stream: process.stderr,
    });
    try {
      const billing = createBillingNamespace();
      spinner.start();
      const days = await fetchDailySandboxUsage(billing, {
        month: argv.month,
      });
      spinner.stop();

      if (argv.output === "json") {
        process.stdout.write(`${JSON.stringify({ data: days }, null, 2)}\n`);
      } else {
        const rows = days.map((day) => [cell(day.date), cell(day.cost)]);
        process.stdout.write(
          `${renderTable(["DATE", "COST (USD)"], rows, process.stdout.isTTY ? process.stdout.columns : undefined)}\n`,
        );
      }
      process.exit(0);
    } catch (error) {
      spinner.stop();
      console.error(
        error instanceof Error
          ? error.message
          : `Unknown error: ${JSON.stringify(error)}`,
      );
      process.exit(1);
    }
  },
};

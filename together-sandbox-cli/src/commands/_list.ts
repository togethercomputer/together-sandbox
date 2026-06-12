import { spawn } from "child_process";
import { once } from "events";
import * as path from "path";
import type { Writable } from "stream";
import type { Page } from "together-sandbox";
import { computeWidths, formatRow, renderTable } from "./_table";

export interface ListArgs {
  limit?: number;
  cursor?: string;
  output?: string;
  ci?: boolean;
}

export interface ListConfig<T> {
  /** Fetch a single page from the SDK. */
  fetchPage: (params: { limit?: number; cursor?: string }) => Promise<Page<T>>;
  /** Uppercase column headers. */
  headers: string[];
  /** Map one item to a row of cells (same order as `headers`). */
  toRow: (item: T) => string[];
}

/**
 * Drive a paginated `list` command. The display mode is decided by TTY
 * detection, not by which flags were passed:
 *
 *  - `--output json` → prints the raw API page (`{ data, next_cursor }`) as
 *    JSON to stdout. Single page.
 *  - stdout is a TTY → open an interactive pager (`less`) immediately and
 *    stream pages into it lazily: the next page is fetched only as you scroll
 *    (pipe backpressure pauses fetching; quitting the pager stops it).
 *  - stdout is not a TTY (piped/redirected), or `--ci` → fetch one page, print
 *    the table to stdout, and print `next_cursor` to stderr.
 *
 * `--limit` / `--cursor` only parametrize the request; they never switch mode.
 */
export async function runList<T>(
  config: ListConfig<T>,
  args: ListArgs,
): Promise<void> {
  if (args.output === "json") {
    const page = await config.fetchPage({
      limit: args.limit,
      cursor: args.cursor,
    });
    process.stdout.write(`${JSON.stringify(page, null, 2)}\n`);
    return;
  }

  if (Boolean(process.stdout.isTTY) && !args.ci) {
    await streamInteractive(config, args);
    return;
  }

  // Non-interactive: one page to stdout, next cursor to stderr.
  const page = await config.fetchPage({
    limit: args.limit,
    cursor: args.cursor,
  });
  process.stdout.write(
    `${renderTable(config.headers, page.data.map(config.toRow))}\n`,
  );
  if (page.next_cursor) {
    process.stderr.write(`next_cursor: ${page.next_cursor}\n`);
  }
}

/**
 * Open a pager and stream pages into it as the user scrolls. Column widths are
 * fixed from the first page so later rows stay aligned without buffering
 * everything. Falls back to streaming straight to stdout if no pager is found.
 */
async function streamInteractive<T>(
  config: ListConfig<T>,
  args: ListArgs,
): Promise<void> {
  const { fetchPage, headers, toRow } = config;
  const { sink, child } = await openPager();

  // `alive` flips to false when the pager exits (user pressed `q`) or its
  // stdin pipe breaks — that's our signal to stop fetching more pages.
  let alive = true;
  const closed = child ? once(child, "close") : Promise.resolve();
  if (child) {
    child.on("close", () => {
      alive = false;
    });
    // Swallow EPIPE when the pager exits before we finish writing.
    sink.on("error", () => {
      alive = false;
    });
  }

  // Write a chunk, honoring backpressure: if the pipe is full, wait until it
  // drains or the pager closes (whichever comes first) before continuing.
  const write = (chunk: string): Promise<void> =>
    new Promise((resolve) => {
      if (!alive) return resolve();
      if (sink.write(chunk)) return resolve();
      const done = () => {
        sink.removeListener("drain", done);
        if (child) child.removeListener("close", done);
        resolve();
      };
      sink.once("drain", done);
      if (child) child.once("close", done);
    });

  let widths: number[] | null = null;
  let cursor = args.cursor;
  try {
    do {
      const page = await fetchPage({ limit: args.limit, cursor });
      if (!alive) break;
      const rows = page.data.map(toRow);
      if (widths === null) {
        widths = computeWidths(headers, rows);
        await write(`${formatRow(headers, widths)}\n`);
      }
      for (const row of rows) {
        if (!alive) break;
        await write(`${formatRow(row, widths)}\n`);
      }
      cursor = page.next_cursor ?? undefined;
    } while (cursor && alive);
  } finally {
    if (child && alive) sink.end();
    await closed;
  }
}

/** Spawn the pager, or return `process.stdout` if none is available. */
async function openPager(): Promise<{
  sink: Writable;
  child: ReturnType<typeof spawn> | null;
}> {
  const pager = process.env.PAGER || "less";
  const parts = pager.split(" ").filter(Boolean);
  const isLess = path.basename(parts[0]) === "less";
  const args = [...parts.slice(1), ...(isLess ? ["-R", "-F", "-X"] : [])];

  try {
    const child = spawn(parts[0], args, {
      stdio: ["pipe", "inherit", "inherit"],
    });
    let failed = false;
    child.on("error", () => {
      failed = true;
    });
    // Give a missing-binary ENOENT a tick to surface before we commit to it.
    await new Promise((resolve) => setImmediate(resolve));
    if (!failed && child.stdin) {
      return { sink: child.stdin, child };
    }
  } catch {
    /* fall through to stdout */
  }
  return { sink: process.stdout, child: null };
}

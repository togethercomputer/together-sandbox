// Plain, awk-parsable column output in the style of `docker ps` / `kubectl get`.
// No box-drawing borders — columns are whitespace-padded so `awk '{print $1}'`
// works. Empty/missing values render as `<none>` to keep columns aligned.

const COLUMN_GAP = "   ";

/** Format a cell value, mapping null/undefined/empty to `<none>`. */
export function cell(value: unknown): string {
  if (value === null || value === undefined || value === "") return "<none>";
  return String(value);
}

/**
 * Render a `tags` map as a compact, awk-safe `k=v,k=v` string. Keys are sorted
 * so the same tags always render identically across rows and runs.
 */
export function formatTags(tags: Record<string, string> | undefined): string {
  const entries = Object.entries(tags ?? {});
  if (entries.length === 0) return cell(undefined);
  return entries
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([k, v]) => `${k}=${v}`)
    .join(",");
}

// Largest-unit-first thresholds for `formatAge`, in seconds. The last entry is
// the fallback, so its threshold must be 1.
const AGE_UNITS: [seconds: number, singular: string, plural: string][] = [
  [60 * 60 * 24 * 365, "yr", "yrs"],
  [60 * 60 * 24 * 30, "mo", "mos"],
  [60 * 60 * 24, "day", "days"],
  [60 * 60, "hr", "hrs"],
  [60, "min", "mins"],
  [1, "sec", "secs"],
];

/**
 * Render an ISO timestamp as a compact age, e.g. "10 secs ago" / "7 mins ago"
 * / "10 hrs ago". Only the largest matching unit is shown — this is a table
 * column, not a precise duration. Unparseable values are passed through so a
 * surprise from the API is visible rather than silently swallowed.
 */
export function formatAge(timestamp: string | null | undefined): string {
  if (timestamp === null || timestamp === undefined || timestamp === "")
    return cell(undefined);
  const then = Date.parse(timestamp);
  if (Number.isNaN(then)) return timestamp;

  // Clamp: a clock skewed slightly ahead of ours should read "0 secs ago", not
  // a negative age.
  const seconds = Math.max(0, Math.floor((Date.now() - then) / 1000));
  for (const [size, singular, plural] of AGE_UNITS) {
    const n = Math.floor(seconds / size);
    if (n >= 1) return `${n} ${n === 1 ? singular : plural} ago`;
  }
  return `0 secs ago`;
}

/** Human-readable byte size, e.g. 134217728 → "128.0MiB". */
export function humanBytes(n: number): string {
  if (!Number.isFinite(n)) return String(n);
  const units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"];
  let value = n;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit++;
  }
  return `${unit === 0 ? value : value.toFixed(1)}${units[unit]}`;
}

/** Column widths sized to fit the headers and the given rows. */
export function computeWidths(headers: string[], rows: string[][]): number[] {
  return headers.map((h, i) =>
    Math.max(h.length, 0, ...rows.map((r) => (r[i] ?? "").length)),
  );
}

/** Format one row, left-padding each cell to the given column widths. */
export function formatRow(cells: string[], widths: number[]): string {
  return cells
    .map((c, i) => (c ?? "").padEnd(widths[i] ?? 0))
    .join(COLUMN_GAP)
    .replace(/\s+$/, "");
}

export interface DescribeSection {
  title: string;
  rows: [string, string][];
}

/**
 * Render `kubectl describe`-style output: flush-left section titles with
 * indented, colon-aligned key/value rows beneath each.
 */
export function renderDescribe(sections: DescribeSection[]): string {
  const blocks = sections
    .filter((s) => s.rows.length > 0)
    .map((section) => {
      const keyWidth = Math.max(0, ...section.rows.map(([k]) => k.length + 1));
      const rows = section.rows.map(
        ([k, v]) => `  ${`${k}:`.padEnd(keyWidth + 1)} ${v}`,
      );
      return [section.title, ...rows].join("\n");
    });
  return blocks.join("\n\n");
}

/** Truncate `s` to `max` columns, marking any elision with a trailing `…`. */
function truncate(s: string, max: number): string {
  if (s.length <= max) return s;
  if (max <= 1) return s.slice(0, Math.max(0, max));
  return `${s.slice(0, max - 1)}…`;
}

/**
 * Shrink the last column so a full row fits inside `maxWidth`, `ps aux`-style.
 * Only the last column gives ground — it is by convention the one holding
 * unbounded values (a command line, a tag map).
 */
export function capLastColumn(widths: number[], maxWidth: number): number[] {
  if (widths.length < 2) return widths;
  const last = widths.length - 1;
  const gaps = COLUMN_GAP.length * (widths.length - 1);
  const fixed = widths.slice(0, last).reduce((a, b) => a + b, 0) + gaps;
  // Leave at least a few columns for the last field even on a narrow tty.
  const cap = Math.max(3, maxWidth - fixed);
  if (widths[last]! <= cap) return widths;
  const capped = widths.slice();
  capped[last] = cap;
  return capped;
}

/** Truncate each cell to its column width, so no row overflows its layout. */
export function fitRow(cells: string[], widths: number[]): string[] {
  return cells.map((c, i) => truncate(c ?? "", widths[i] ?? 0));
}

/**
 * Render an uppercase header row + rows as space-aligned columns.
 *
 * When `maxWidth` is given (typically the terminal width), the last column is
 * truncated so every line fits on one row. Omit it — e.g. when output is piped
 * — to print full, untruncated cells.
 */
export function renderTable(
  headers: string[],
  rows: string[][],
  maxWidth?: number,
): string {
  let widths = computeWidths(headers, rows);
  if (maxWidth !== undefined) widths = capLastColumn(widths, maxWidth);

  return [
    formatRow(headers, widths),
    ...rows.map((r) => formatRow(fitRow(r, widths), widths)),
  ].join("\n");
}

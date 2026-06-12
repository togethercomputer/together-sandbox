// Plain, awk-parsable column output in the style of `docker ps` / `kubectl get`.
// No box-drawing borders — columns are whitespace-padded so `awk '{print $1}'`
// works. Empty/missing values render as `<none>` to keep columns aligned.

const COLUMN_GAP = "   ";

/** Format a cell value, mapping null/undefined/empty to `<none>`. */
export function cell(value: unknown): string {
  if (value === null || value === undefined || value === "") return "<none>";
  return String(value);
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

/** Render an uppercase header row + rows as space-aligned columns. */
export function renderTable(headers: string[], rows: string[][]): string {
  const widths = computeWidths(headers, rows);
  return [
    formatRow(headers, widths),
    ...rows.map((r) => formatRow(r, widths)),
  ].join("\n");
}

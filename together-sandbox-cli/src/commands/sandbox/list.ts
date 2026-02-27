import ora from "ora";
import Table from "cli-table3";
import { API, api, getInferredApiKey } from "@together-sandbox/sdk";

type SandboxListOpts = {
  tags?: string[];
  orderBy?: "inserted_at" | "updated_at";
  direction?: "asc" | "desc";
  status?: "running";
  page?: number;
  pageSize?: number;
};

type OutputFormat = {
  field: string;
  header: string;
  width?: number;
};

const TABLE_FORMAT: OutputFormat[] = [
  { field: "id", header: "ID", width: 24 },
  { field: "title", header: "TITLE", width: 40 },
  { field: "privacy", header: "PRIVACY", width: 10 },
  { field: "tags", header: "TAGS", width: 20 },
  { field: "updated_at", header: "AGE" },
];

function formatAge(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `${days}d`;
  }
  if (hours > 0) {
    return `${hours}h`;
  }
  if (minutes > 0) {
    return `${minutes}m`;
  }
  return `${seconds}s`;
}

export async function listSandboxes(
  outputFields?: string,
  listOpts: SandboxListOpts & { since?: string } = {},
  showHeaders = true,
  limit?: number
) {
  const api = new API({ apiKey: getInferredApiKey() });
  const spinner = ora("Fetching sandboxes...").start();

  try {
    let allSandboxes: api.Sandbox[] = [];
    let totalCount = 0;
    let currentPage = listOpts.page ?? 1;
    const pageSize = listOpts.pageSize ?? 50; // API's maximum page size

    // Default limit to 100 if not specified, unless since is provided
    if (limit === undefined) {
      limit = listOpts.since ? Infinity : 100;
    }

    // If since is provided, ensure we're ordering by inserted_at desc
    if (listOpts.since) {
      listOpts.orderBy = "inserted_at";
      listOpts.direction = "desc";
    }

    // Parse the since date if provided
    const sinceDate = listOpts.since ? new Date(listOpts.since) : null;
    if (sinceDate && isNaN(sinceDate.getTime())) {
      throw new Error(
        `Invalid date format for 'since': ${listOpts.since}. Use ISO format (e.g., '2023-01-01T00:00:00Z').`
      );
    }

    while (true) {
      const result = await api.listSandboxes({
        tags: listOpts.tags?.join(","),
        order_by: listOpts.orderBy,
        direction: listOpts.direction,
        status: listOpts.status,
        page: currentPage,
        page_size: pageSize,
      });

      const { sandboxes, pagination } = result;

      if (sandboxes.length === 0) {
        break;
      }

      totalCount = pagination.total_records;

      // Filter sandboxes by the since date if provided
      const filteredSandboxes = sinceDate
        ? sandboxes.filter(
            (sandbox) => new Date(sandbox.created_at) >= sinceDate
          )
        : sandboxes;

      // If we're using since and ordering by inserted_at desc, stop once we
      // encounter a sandbox older than the since date
      if (
        sinceDate &&
        listOpts.orderBy === "inserted_at" &&
        listOpts.direction === "desc" &&
        sandboxes.some((sandbox) => new Date(sandbox.created_at) < sinceDate)
      ) {
        const newSandboxes = filteredSandboxes.filter(
          (sandbox) =>
            !allSandboxes.some((existing) => existing.id === sandbox.id)
        );
        allSandboxes = [...allSandboxes, ...newSandboxes];
        break;
      }

      const newSandboxes = filteredSandboxes.filter(
        (sandbox) =>
          !allSandboxes.some((existing) => existing.id === sandbox.id)
      );
      allSandboxes = [...allSandboxes, ...newSandboxes];

      spinner.text = `Fetching sandboxes... (${allSandboxes.length}${
        limit !== Infinity
          ? `/${Math.min(limit, totalCount)}`
          : `/${totalCount}`
      })`;

      // Stop if we've reached the total count or the limit
      if (allSandboxes.length >= limit || pagination.next_page == null) {
        break;
      }

      currentPage = pagination.next_page;
    }

    // Apply limit after fetching all sandboxes
    if (limit !== Infinity) {
      allSandboxes = allSandboxes.slice(0, limit);
    }

    spinner.stop();

    if (outputFields) {
      // Custom output format - just print the requested fields
      const fields = outputFields.split(",").map((f) => f.trim());

      if (showHeaders) {
        // eslint-disable-next-line no-console
        console.log(fields.join("\t"));
      }

      allSandboxes.forEach((sandbox) => {
        const values = fields.map((field) => {
          const value = sandbox[field as keyof typeof sandbox];
          if (Array.isArray(value)) {
            return value.join(",");
          }
          return value?.toString() ?? "";
        });
        // eslint-disable-next-line no-console
        console.log(values.join("\t"));
      });

      // eslint-disable-next-line no-console
      console.error(
        listOpts.since
          ? `\nShowing ${allSandboxes.length} sandboxes created since ${listOpts.since}`
          : `\nShowing ${allSandboxes.length} of ${totalCount} sandboxes`
      );

      return;
    }

    // Table output format
    const table = new Table({
      head: showHeaders ? TABLE_FORMAT.map((f) => f.header) : [],
      colWidths: TABLE_FORMAT.map((f) => f.width ?? null),
      style: {
        head: ["bold"],
        border: [],
      },
      chars: {
        top: "",
        "top-mid": "",
        "top-left": "",
        "top-right": "",
        bottom: "",
        "bottom-mid": "",
        "bottom-left": "",
        "bottom-right": "",
        left: "",
        "left-mid": "",
        right: "",
        "right-mid": "",
        mid: "",
        "mid-mid": "",
        middle: " ",
      },
    });

    allSandboxes.forEach((sandbox) => {
      const row = TABLE_FORMAT.map((format) => {
        const value = sandbox[format.field as keyof typeof sandbox];
        if (format.field === "updated_at" && typeof value === "string") {
          return formatAge(new Date(value));
        }
        if (Array.isArray(value)) {
          return value.join(",");
        }
        return value?.toString() ?? "";
      });
      table.push(row);
    });

    // eslint-disable-next-line no-console
    console.log(table.toString());

    if (limit !== Infinity && totalCount > allSandboxes.length) {
      // eslint-disable-next-line no-console
      console.error(
        listOpts.since
          ? `\nShowing ${allSandboxes.length} sandboxes created since ${listOpts.since}`
          : `\nShowing ${allSandboxes.length} of ${totalCount} sandboxes`
      );
    }
  } catch (error) {
    spinner.fail("Failed to fetch sandboxes");
    throw error;
  }
}

import type * as yargs from "yargs";
import * as path from "path";
import { TogetherSandbox } from "together-sandbox";
import type { CreateSnapshotParams, Snapshot } from "together-sandbox";
import ora from "ora";
import { runList, type ListArgs } from "./_list";
import {
  cell,
  formatAge,
  formatTagLines,
  formatTags,
  humanBytes,
  renderDescribe,
} from "./_table";
import { parseKeyValues } from "./_exec";
import { examples } from "./_help";

function describeSnapshot(s: Snapshot): {
  title: string;
  rows: [string, string][];
}[] {
  return [
    {
      title: "Identity",
      rows: [
        ["ID", cell(s.id)],
        ["Organization", cell(s.organization_id)],
        ["Project", cell(s.project_id)],
        ["Tags", formatTagLines(s.tags)],
      ],
    },
    {
      title: "Storage",
      rows: [
        ["Size", humanBytes(s.byte_size)],
        ["Memory snapshot", cell(s.memory)],
      ],
    },
    {
      title: "Retention",
      rows: [
        ["TTL", s.ttl !== null && s.ttl !== undefined ? `${s.ttl}s` : cell(undefined)],
      ],
    },
    {
      title: "Lifecycle",
      rows: [
        ["Created", cell(s.created_at)],
        // A retired snapshot can no longer create sandboxes and is eventually
        // deleted, once no sandbox still references it.
        ["Retired", cell(s.retired_at)],
        ["Updated", cell(s.updated_at)],
      ],
    },
  ];
}


export type CreateArgs = {
  context?: string;
  dockerfile?: string;
  image?: string;
  alias?: string;
  ci?: boolean;
};

export const createCommand: yargs.CommandModule<
  Record<string, never>,
  CreateArgs
> = {
  command: "create",
  describe: "Create a snapshot from a build context or Docker image.",
  builder: (yargs) =>
    yargs
      .option("context", {
        type: "string",
        describe: "Path to the Docker build context directory",
      })
      .option("dockerfile", {
        type: "string",
        describe: "Path to the Dockerfile (only with --context)",
      })
      .option("image", {
        type: "string",
        describe: "Docker image reference (e.g. node:20)",
      })
      .option("alias", {
        type: "string",
        describe: "Alias for the snapshot (namespace@tag or just tag)",
      })
      .option("ci", {
        type: "boolean",
        default: false,
        describe: "CI mode: plain stdout, no spinner",
      })
      .epilogue(
        examples([
          {
            describe: "Build the current directory",
            command: "$0 snapshots create --context .",
          },
          {
            describe: "Build with a custom Dockerfile and alias the result",
            command:
              "$0 snapshots create --context ./app --dockerfile ./app/Dockerfile.prod --alias my-app@v1",
          },
          {
            describe: "Register a public image as a snapshot, no local build",
            command: "$0 snapshots create --image node:22",
          },
          {
            describe: "CI mode: stdout is just the snapshot id",
            command: "SNAPSHOT_ID=$($0 snapshots create --ci --context .)",
          },
        ]),
      )
      .check((argv) => {
        if (!argv.context && !argv.image)
          throw new Error("Provide either --context or --image.");
        if (argv.context && argv.image)
          throw new Error("--context and --image are mutually exclusive.");
        if (argv.dockerfile && !argv.context)
          throw new Error("--dockerfile requires --context.");
        return true;
      }) as yargs.Argv<CreateArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    const spinner = ora({ stream: process.stdout });

    if (!argv.ci) {
      spinner.start();
    }

    try {
      let params: CreateSnapshotParams;
      const onProgress = (event: { output: string }) => {
        if (argv.ci) {
          console.log(event.output);
        } else {
          spinner.text = event.output;
        }
      };

      if (argv.context) {
        const resolvedContext = path.resolve(argv.context);
        const resolvedDockerfile = argv.dockerfile
          ? path.resolve(argv.dockerfile)
          : undefined;
        params = {
          context: resolvedContext,
          dockerfile: resolvedDockerfile,
          alias: argv.alias,
          onProgress,
        };
      } else {
        params = {
          image: argv.image!,
          alias: argv.alias,
          onProgress,
        };
      }

      const result = await sdk.snapshots.create(params);
      if (argv.ci) {
        // Guarantee we have written the snapshot id as last output before letting process exit.
        // Doing console.log and sync exit, can drop the last log
        await new Promise<void>((resolve, reject) =>
          process.stdout.write(
            `${result.snapshotId}
`,
            (err) => (err ? reject(err) : resolve()),
          ),
        );
      } else {
        spinner.succeed(
          `Snapshot created: ${result.snapshotId}${result.alias ? " (" + result.alias + ")" : ""}`,
        );
      }
      process.exit(0);
    } catch (error) {
      if (!argv.ci) {
        spinner.fail();
      }

      console.error(
        error instanceof Error
          ? error.message
          : `Unknown error: ${JSON.stringify(error)}`,
      );
      process.exit(1);
    }
  },
};

interface SnapshotListArgs extends ListArgs {
  excludeRetired?: boolean;
  tag?: string[];
}

export const listCommand: yargs.CommandModule<
  Record<string, never>,
  SnapshotListArgs
> = {
  command: "list",
  describe: "List snapshots.",
  builder: (yargs) =>
    yargs
      .option("limit", {
        type: "number",
        describe: "Maximum number of items per page (1–100)",
      })
      .option("cursor", {
        type: "string",
        describe:
          "Resume from a cursor (from a prior page); shows a single page and " +
          "disables the interactive pager",
      })
      .option("exclude-retired", {
        type: "boolean",
        default: false,
        describe: "Hide retired snapshots (they are included by default)",
      })
      .option("tag", {
        type: "string",
        array: true,
        describe:
          "Only show snapshots carrying this tag, KEY=VALUE (repeatable; all must match)",
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
            describe: "Page through every snapshot in your pager",
            command: "$0 snapshots list",
          },
          {
            describe: "Only active snapshots tagged env=prod",
            command: "$0 snapshots list --exclude-retired --tag env=prod",
          },
          {
            describe:
              "Fetch one specific page (the next cursor is printed on stderr)",
            command: "$0 snapshots list --limit 50 --cursor <cursor>",
          },
          {
            describe: "Machine-readable single page: { data, nextCursor }",
            command: "$0 snapshots list --ci -o json",
          },
        ]),
      ) as unknown as yargs.Argv<SnapshotListArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    try {
      const excludeRetired = argv.excludeRetired;
      const tags = parseKeyValues(argv.tag, "--tag");
      await runList(
        {
          fetchPage: (params) =>
            sdk.snapshots.list({ ...params, excludeRetired, tags }),
          // TAGS is last: it is the only unbounded-width column, and
          // `renderTable` truncates the final column to fit the terminal.
          headers: ["ID", "SIZE", "MEMORY", "RETIRED", "AGE", "TAGS"],
          toRow: (s) => [
            cell(s.id),
            humanBytes(s.byte_size),
            cell(s.memory),
            formatAge(s.retired_at),
            formatAge(s.created_at),
            formatTags(s.tags),
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

interface GetArgs {
  ref: string;
  output?: string;
}

export const getCommand: yargs.CommandModule<Record<string, never>, GetArgs> = {
  command: "get <ref>",
  describe: "Show details for a single snapshot, by id or @alias.",
  builder: (yargs) =>
    yargs
      .positional("ref", {
        type: "string",
        describe: "Snapshot id, or @alias to look up by alias",
        demandOption: true,
      })
      .option("output", {
        alias: "o",
        type: "string",
        choices: ["text", "json"] as const,
        default: "text",
        describe: "Output format",
      })
      .epilogue(
        examples([
          { describe: "Look up by id", command: "$0 snapshots get <snapshot-id>" },
          { describe: "Look up by alias", command: "$0 snapshots get @my-app@v1" },
          {
            describe: "Machine-readable output",
            command: "$0 snapshots get <snapshot-id> -o json",
          },
        ]),
      ) as unknown as yargs.Argv<GetArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    try {
      // A leading `@` selects alias lookup (matches the API's /snapshots/@{alias}
      // convention); anything else is treated as a raw snapshot id.
      const snapshot = argv.ref.startsWith("@")
        ? await sdk.snapshots.getByAlias(argv.ref.slice(1))
        : await sdk.snapshots.getById(argv.ref);

      if (argv.output === "json") {
        process.stdout.write(`${JSON.stringify(snapshot, null, 2)}\n`);
      } else {
        process.stdout.write(`${renderDescribe(describeSnapshot(snapshot))}\n`);
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

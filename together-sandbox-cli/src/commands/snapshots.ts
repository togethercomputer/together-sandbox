import type * as yargs from "yargs";
import * as path from "path";
import { TogetherSandbox } from "together-sandbox";
import type { CreateSnapshotParams, Snapshot } from "together-sandbox";
import ora from "ora";
import { runList, type ListArgs } from "./_list";
import { cell, humanBytes, renderDescribe } from "./_table";

function describeSnapshot(s: Snapshot): {
  title: string;
  rows: [string, string][];
}[] {
  return [
    {
      title: "Identity",
      rows: [
        ["ID", cell(s.id)],
        ["Project", cell(s.project_id)],
      ],
    },
    {
      title: "Storage",
      rows: [
        ["Size", humanBytes(s.byte_size)],
        ["Memory snapshot", cell(s.includes_memory_snapshot)],
      ],
    },
    {
      title: "Flags",
      rows: [
        ["Protected", cell(s.protected)],
        ["Optimized", cell(s.optimized)],
      ],
    },
    {
      title: "Lifecycle",
      rows: [
        ["Created", cell(s.created_at)],
        ["Optimized at", cell(s.optimized_at)],
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

export const listCommand: yargs.CommandModule<Record<string, never>, ListArgs> =
  {
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
        }) as yargs.Argv<ListArgs>,

    handler: async (argv) => {
      const sdk = new TogetherSandbox();
      try {
        await runList(
          {
            fetchPage: (params) => sdk.snapshots.list(params),
            headers: ["ID", "SIZE", "OPTIMIZED", "CREATED"],
            toRow: (s) => [
              cell(s.id),
              humanBytes(s.byte_size),
              cell(s.optimized),
              cell(s.created_at),
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
      }) as unknown as yargs.Argv<GetArgs>,

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

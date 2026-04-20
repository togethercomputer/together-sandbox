import type * as yargs from "yargs";
import { TogetherSandbox } from "@together-sandbox/sdk";
import ora from "ora";

export type CreateSnapshotArgs = {
  directory: string;
  alias?: string;
  memorySnapshot?: boolean;
};

export const createSnapshotCommand: yargs.CommandModule<
  Record<string, never>,
  CreateSnapshotArgs
> = {
  command: "create <directory>",
  describe:
    "Build a snapshot from a directory. This snapshot can be used to create sandboxes.",
  builder: (yargs: yargs.Argv) =>
    yargs
      .option("alias", {
        describe:
          "Alias that should point to the created snapshot. Alias namespace defaults to directory name, but you can explicitly pass `namespace@alias`",
        type: "string",
      })
      /*
      // This is not yet supported due to a Nydus bug. We'll open up for this when it works.
      .option("memory-snapshot", {
        describe:
          "Create a memory snapshot by starting the sandbox and capturing its state",
        type: "boolean",
      })
        */
      .positional("directory", {
        describe: "Path to the project that we'll create a snapshot from",
        type: "string",
        demandOption: "Path to the project is required",
      }),

  handler: async (argv) => {
    return createSnapshot(argv);
  },
};

/**
 * Build a Together Sandbox Snapshot using Docker for use in gvisor-based sandboxes.
 * @param argv arguments to csb build command
 */
export async function createSnapshot(
  argv: yargs.ArgumentsCamelCase<CreateSnapshotArgs>,
): Promise<void> {
  const sdk = new TogetherSandbox();
  const createSnapshotSpinner = ora({ stream: process.stdout });

  createSnapshotSpinner.start();

  try {
    const result = await sdk.snapshots.create({
      directory: argv.directory,
      memorySnapshot: argv.memorySnapshot,
      alias: argv.alias,
      onProgress: (event) => {
        createSnapshotSpinner.text = event.output;
      },
    });
    createSnapshotSpinner.succeed(
      `Snapshot created: ${result.alias || result.snapshotId}`,
    );
    process.exit(0);
  } catch (error) {
    createSnapshotSpinner.fail();
    console.error(
      error instanceof Error
        ? error.message
        : `Unknown error: ${JSON.stringify(error)}`,
    );
    process.exit(1);
  }
}

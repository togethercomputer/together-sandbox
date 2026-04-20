import type * as yargs from "yargs";
import { TogetherSandbox } from "@together-sandbox/sdk";
import ora from "ora";

export type CreateSnapshotArgs = {
  dockerFile?: string;
  image?: string;
  alias?: string;
  // memorySnapshot?: boolean; // still commented out
};

export const createSnapshotCommand: yargs.CommandModule<
  Record<string, never>,
  CreateSnapshotArgs
> = {
  command: "create",
  describe:
    "Build a snapshot from a directory. This snapshot can be used to create sandboxes.",
  builder: (yargs: yargs.Argv) =>
    yargs
      .option("dockerFile", {
        describe: "Path to a Dockerfile to build a snapshot from",
        type: "string",
      })
      .option("image", {
        describe: "Docker image name or reference to create a snapshot from",
        type: "string",
      })
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
      .check((argv) => {
        if (!argv.dockerFile && !argv.image) {
          throw new Error("Provide either --dockerFile or --image");
        }
        if (argv.dockerFile && argv.image) {
          throw new Error("--dockerFile and --image are mutually exclusive");
        }
        return true;
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
    const params = {
      alias: argv.alias,
      onProgress: (event: { output: string }) => {
        createSnapshotSpinner.text = event.output;
      },
    };
    const result = argv.dockerFile
      ? await sdk.snapshots.fromDockerFile(argv.dockerFile, params)
      : await sdk.snapshots.fromImage(argv.image!, params);
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

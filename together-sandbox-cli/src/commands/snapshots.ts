import type * as yargs from "yargs";
import * as path from "path";
import { TogetherSandbox } from "@together-sandbox/sdk";
import ora from "ora";

export type SnapshotOptions = {
  alias?: string;
  // memorySnapshot?: boolean; // not yet supported
};

export type FromBuildArgs = {
  dockerContext: string;
  dockerFile?: string;
} & SnapshotOptions;

export type FromImageArgs = {
  image: string;
} & SnapshotOptions;

function addSnapshotOptions<T>(
  yargs: yargs.Argv<T>,
): yargs.Argv<T & SnapshotOptions> {
  return yargs.option("alias", {
    describe:
      "Alias for the snapshot. Namespace defaults to the image/directory name, or pass `namespace@alias` explicitly",
    type: "string",
  });
  // When memorySnapshot is ready, add it here
}

export const fromBuildCommand: yargs.CommandModule<
  Record<string, never>,
  FromBuildArgs
> = {
  command: "from-build <dockerContext>",
  describe: "Build a snapshot from a Dockerfile.",
  builder: (yargs: yargs.Argv) =>
    addSnapshotOptions(
      yargs
        .positional("dockerContext", {
          describe: "Path to the Docker build context directory",
          type: "string",
          demandOption: true,
        })
        .option("dockerFile", {
          describe: "Path to a Dockerfile to build a snapshot from",
          type: "string",
        }),
    ) as yargs.Argv<FromBuildArgs>,

  handler: async (argv) => {
    return snapshotFromBuild(argv);
  },
};

export const fromImageCommand: yargs.CommandModule<
  Record<string, never>,
  FromImageArgs
> = {
  command: "from-image <image>",
  describe: "Create a snapshot from a Docker image.",
  builder: (yargs: yargs.Argv) =>
    addSnapshotOptions(
      yargs.positional("image", {
        describe: "Docker image name or reference to create a snapshot from",
        type: "string",
        demandOption: true,
      }),
    ) as yargs.Argv<FromImageArgs>,

  handler: async (argv) => {
    return snapshotFromImage(argv);
  },
};

/**
 * Build a Together Sandbox Snapshot from a Dockerfile.
 * @param argv arguments to from-build command
 */
async function snapshotFromBuild(
  argv: yargs.ArgumentsCamelCase<FromBuildArgs>,
): Promise<void> {
  const sdk = new TogetherSandbox();
  const spinner = ora({ stream: process.stdout });

  spinner.start();

  try {
    const resolvedDockerContext = path.resolve(argv.dockerContext);
    const resolvedDockerFile = argv.dockerFile
      ? path.resolve(argv.dockerFile)
      : undefined;

    const result = await sdk.snapshots.fromBuild(resolvedDockerContext, {
      dockerfile: resolvedDockerFile,
      alias: argv.alias,
      onProgress: (event: { output: string }) => {
        spinner.text = event.output;
      },
    });
    spinner.succeed(`Snapshot created: ${result.alias || result.snapshotId}`);
    process.exit(0);
  } catch (error) {
    spinner.fail();
    console.error(
      error instanceof Error
        ? error.message
        : `Unknown error: ${JSON.stringify(error)}`,
    );
    process.exit(1);
  }
}

/**
 * Create a Together Sandbox Snapshot from a Docker image.
 * @param argv arguments to from-image command
 */
async function snapshotFromImage(
  argv: yargs.ArgumentsCamelCase<FromImageArgs>,
): Promise<void> {
  const sdk = new TogetherSandbox();
  const spinner = ora({ stream: process.stdout });

  spinner.start();

  try {
    const params = {
      alias: argv.alias,
      onProgress: (event: { output: string }) => {
        spinner.text = event.output;
      },
    };
    const result = await sdk.snapshots.fromImage(argv.image, params);
    spinner.succeed(`Snapshot created: ${result.alias || result.snapshotId}`);
    process.exit(0);
  } catch (error) {
    spinner.fail();
    console.error(
      error instanceof Error
        ? error.message
        : `Unknown error: ${JSON.stringify(error)}`,
    );
    process.exit(1);
  }
}

import type * as yargs from "yargs";
import * as path from "path";
import { TogetherSandbox } from "@together-sandbox/sdk";
import type { CreateSnapshotParams } from "@together-sandbox/sdk";
import ora from "ora";

export type CreateArgs = {
  context?: string;
  dockerfile?: string;
  image?: string;
  alias?: string;
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

    spinner.start();

    try {
      let params: CreateSnapshotParams;

      if (argv.context) {
        const resolvedContext = path.resolve(argv.context);
        const resolvedDockerfile = argv.dockerfile
          ? path.resolve(argv.dockerfile)
          : undefined;

        params = {
          context: resolvedContext,
          dockerfile: resolvedDockerfile,
          alias: argv.alias,
          onProgress: (event: { output: string }) => {
            spinner.text = event.output;
          },
        };
      } else {
        params = {
          image: argv.image!,
          alias: argv.alias,
          onProgress: (event: { output: string }) => {
            spinner.text = event.output;
          },
        };
      }

      const result = await sdk.snapshots.create(params);
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
  },
};

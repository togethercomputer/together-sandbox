import type * as yargs from "yargs";
import { TogetherSandbox } from "together-sandbox";
import {
  getExecOutput,
  listExecs,
  streamExecOutput,
  type ExecTarget,
} from "./_exec";
import { cell, renderTable } from "./_table";

/**
 * Resolve a running sandbox's agent connection details, erroring if the
 * sandbox is not running or exposes no agent endpoint.
 */
async function resolveTarget(
  sdk: TogetherSandbox,
  sandboxId: string,
): Promise<ExecTarget> {
  const sandbox = await sdk.sandboxes.get(sandboxId);
  if (sandbox.status !== "running") {
    throw new Error(
      `sandbox ${sandboxId} is not running (status: ${sandbox.status})`,
    );
  }
  if (!sandbox.agentUrl || !sandbox.agentToken) {
    throw new Error(`sandbox ${sandboxId} has no agent connection details`);
  }
  return { agent: sandbox.agentUrl, token: sandbox.agentToken };
}

interface LsArgs {
  id: string;
  output?: string;
}

export const lsCommand: yargs.CommandModule<Record<string, never>, LsArgs> = {
  command: "ls <id>",
  aliases: ["list"],
  describe: "List execs running (or recently run) in a sandbox.",
  builder: (yargs) =>
    yargs
      .positional("id", {
        type: "string",
        describe: "Sandbox id",
        demandOption: true,
      })
      .option("output", {
        alias: "o",
        type: "string",
        choices: ["table", "json"] as const,
        default: "table",
        describe: "Output format",
      }) as unknown as yargs.Argv<LsArgs>,

  handler: async (argv) => {
    try {
      const sdk = new TogetherSandbox();
      const target = await resolveTarget(sdk, argv.id);
      const execs = await listExecs(target);

      if (argv.output === "json") {
        process.stdout.write(`${JSON.stringify(execs, null, 2)}\n`);
        process.exit(0);
      }

      const rows = execs.map((e) => [
        cell(e.id),
        cell(e.status),
        cell(e.pty),
        cell(e.exitCode >= 0 ? e.exitCode : undefined),
        // Collapse whitespace so a multi-line command stays a single row.
        cell([e.command, ...e.args].join(" ").replace(/\s+/g, " ").trim()),
      ]);
      // On a tty, truncate the COMMAND column so each exec is one line.
      const maxWidth = process.stdout.isTTY
        ? process.stdout.columns
        : undefined;
      process.stdout.write(
        `${renderTable(["ID", "STATUS", "PTY", "EXIT", "COMMAND"], rows, maxWidth)}\n`,
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

interface LogsArgs {
  id: string;
  execId: string;
  follow?: boolean;
}

export const logsCommand: yargs.CommandModule<Record<string, never>, LogsArgs> =
  {
    command: "logs <id> <execId>",
    describe: "Print the output of an exec in a sandbox.",
    builder: (yargs) =>
      yargs
        .positional("id", {
          type: "string",
          describe: "Sandbox id",
          demandOption: true,
        })
        .positional("execId", {
          type: "string",
          describe: "Exec id",
          demandOption: true,
        })
        .option("follow", {
          alias: "f",
          type: "boolean",
          default: false,
          describe: "Follow output as it is produced until the exec exits",
        }) as unknown as yargs.Argv<LogsArgs>,

    handler: async (argv) => {
      try {
        const sdk = new TogetherSandbox();
        const target = await resolveTarget(sdk, argv.id);

        if (argv.follow) {
          await streamExecOutput(target, argv.execId);
        } else {
          const frames = await getExecOutput(target, argv.execId);
          for (const frame of frames) {
            if (!frame.output) continue;
            if (frame.type === "stderr") process.stderr.write(frame.output);
            else process.stdout.write(frame.output);
          }
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

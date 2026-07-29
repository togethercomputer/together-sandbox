import type * as yargs from "yargs";
import { TogetherSandbox } from "together-sandbox";
import {
  createExec,
  fullCommand,
  getExecOutput,
  listExecs,
  parseEnv,
  resolveTarget,
  runExec,
  streamExecOutput,
  type ExecSpec,
} from "./_exec";
import { cell, renderTable } from "./_table";
import { examples } from "./_help";

// ─── Shared options for the commands that start a process ────────────────────

interface ExecProcessArgs {
  id: string;
  command: string[];
  cwd?: string;
  env?: string[];
  user?: string;
}

/** Options describing *what* to execute, shared by `create` and `run`. */
function processOptions<T>(yargs: yargs.Argv<T>) {
  return yargs
    .positional("id", {
      type: "string",
      describe: "Sandbox id",
      demandOption: true,
    })
    .positional("command", {
      type: "string",
      describe: "Command and arguments (use -- to separate from flags)",
      array: true,
      default: [] as string[],
    })
    .option("cwd", { type: "string", describe: "Working directory" })
    .option("env", {
      type: "string",
      array: true,
      describe: "Environment variable KEY=VALUE (repeatable)",
    })
    .option("user", {
      type: "string",
      describe: 'Run as user[:group] (e.g. "1000:1000" or "node")',
    })
    .check((argv) => {
      if (fullCommand(argv as Record<string, unknown>).length === 0)
        throw new Error("Provide a command to run, e.g. -- ls -la");
      return true;
    });
}

/** Build the exec spec from a parsed argv. */
function specFrom(argv: ExecProcessArgs): ExecSpec {
  const [cmd, ...args] = fullCommand(argv as unknown as Record<string, unknown>);
  return { cmd, args, cwd: argv.cwd, env: parseEnv(argv.env), user: argv.user };
}

function fail(error: unknown): never {
  console.error(
    error instanceof Error
      ? error.message
      : `Unknown error: ${JSON.stringify(error)}`,
  );
  process.exit(1);
}

// ─── create ──────────────────────────────────────────────────────────────────

export const createCommand: yargs.CommandModule<
  Record<string, never>,
  ExecProcessArgs
> = {
  command: "create <id> [command..]",
  describe:
    "Start a command in a sandbox and print its exec id, without attaching.",
  builder: (yargs) =>
    processOptions(yargs).epilogue(
      examples(
        [
          {
            describe: "Start a build and get its exec id back",
            command: "$0 sandbox exec create <sandbox-id> -- npm run build",
          },
          {
            describe: "Capture the id for later, in a script",
            command:
              "EXEC_ID=$($0 sandbox exec create <sandbox-id> -- npm run build)",
          },
          {
            describe: "Set the working directory and environment",
            command:
              "$0 sandbox exec create <sandbox-id> --cwd /app --env NODE_ENV=test -- npm test",
          },
        ],
        "The process starts immediately and keeps running after this command\n" +
          "exits. Read its output with `$0 sandbox exec logs <sandbox-id> <exec-id>`.",
      ),
    ) as unknown as yargs.Argv<ExecProcessArgs>,

  handler: async (argv) => {
    try {
      const sdk = new TogetherSandbox();
      const target = await resolveTarget(sdk, argv.id);
      const exec = await createExec(target, specFrom(argv), false);
      // Only the id on stdout, so `EXEC_ID=$(...)` works.
      process.stdout.write(`${exec.id}\n`);
      process.exit(0);
    } catch (error) {
      fail(error);
    }
  },
};

// ─── run ─────────────────────────────────────────────────────────────────────

interface RunArgs extends ExecProcessArgs {
  interactive?: boolean;
  tty?: boolean;
}

export const runCommand: yargs.CommandModule<Record<string, never>, RunArgs> = {
  command: "run <id> [command..]",
  describe: "Run a command in a sandbox and stream it, ssh-style.",
  builder: (yargs) =>
    processOptions(yargs)
      .option("interactive", {
        alias: "i",
        type: "boolean",
        default: false,
        describe: "Keep stdin open / run interactively",
      })
      .option("tty", {
        alias: "t",
        type: "boolean",
        default: false,
        describe: "Allocate a pseudo-TTY (interactive session)",
      })
      .epilogue(
        examples(
          [
            {
              describe: "One-shot command",
              command: "$0 sandbox exec run <sandbox-id> -- ls -la /app",
            },
            {
              describe: "Interactive shell (PTY over a websocket)",
              command: "$0 sandbox exec run <sandbox-id> -it -- bash",
            },
            {
              describe: "Pipe stdin into the remote command",
              command:
                "cat data.json | $0 sandbox exec run <sandbox-id> -i -- jq .name",
            },
          ],
          "Use `--` to separate the command from CLI flags.\n" +
            "The sandbox must be running. The CLI exits with the remote command's exit code.",
        ),
      ) as unknown as yargs.Argv<RunArgs>,

  handler: async (argv) => {
    try {
      const sdk = new TogetherSandbox();
      const target = await resolveTarget(sdk, argv.id);
      const exitCode = await runExec(target, specFrom(argv), {
        interactive: argv.interactive,
        tty: argv.tty,
      });
      process.exit(exitCode);
    } catch (error) {
      fail(error);
    }
  },
};

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
      })
      .epilogue(
        examples([
          {
            describe: "List execs running (or recently run) in a sandbox",
            command: "$0 sandbox exec ls <sandbox-id>",
          },
          {
            describe: "Machine-readable output",
            command: "$0 sandbox exec ls <sandbox-id> -o json",
          },
        ]),
      ) as unknown as yargs.Argv<LsArgs>,

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
        })
        .epilogue(
          examples(
            [
              {
                describe: "Print everything the exec has produced so far",
                command: "$0 sandbox exec logs <sandbox-id> <exec-id>",
              },
              {
                describe: "Stream output until the exec exits",
                command: "$0 sandbox exec logs <sandbox-id> <exec-id> -f",
              },
            ],
            "Find exec ids with `$0 sandbox exec ls <sandbox-id>`.",
          ),
        ) as unknown as yargs.Argv<LogsArgs>,

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

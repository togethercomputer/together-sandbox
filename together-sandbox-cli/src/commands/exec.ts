import type * as yargs from "yargs";
import { TogetherSandbox } from "together-sandbox";
import { fullCommand, parseEnv, runExec, type ExecSpec } from "./_exec";

interface ExecArgs {
  id: string;
  command: string[];
  interactive?: boolean;
  tty?: boolean;
  cwd?: string;
  env?: string[];
  user?: string;
}

export const execCommand: yargs.CommandModule<Record<string, never>, ExecArgs> =
  {
    command: "exec <id> [command..]",
    describe: "Run a command inside a running sandbox (docker exec-style).",
    builder: (yargs) =>
      yargs
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
            throw new Error("Provide a command to run, e.g. exec <id> -- ls -la");
          return true;
        }) as unknown as yargs.Argv<ExecArgs>,

    handler: async (argv) => {
      try {
        const sdk = new TogetherSandbox();
        const sandbox = await sdk.sandboxes.get(argv.id);
        if (sandbox.status !== "running") {
          throw new Error(
            `sandbox ${argv.id} is not running (status: ${sandbox.status})`,
          );
        }
        if (!sandbox.agent_url || !sandbox.agent_token) {
          throw new Error(`sandbox ${argv.id} has no agent connection details`);
        }

        const [cmd, ...args] = fullCommand(argv as Record<string, unknown>);
        const spec: ExecSpec = {
          cmd,
          args,
          cwd: argv.cwd,
          env: parseEnv(argv.env),
          user: argv.user,
        };
        const target = { agent: sandbox.agent_url, token: sandbox.agent_token };

        const exitCode = await runExec(target, spec, {
          interactive: argv.interactive,
          tty: argv.tty,
        });

        process.exit(exitCode);
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

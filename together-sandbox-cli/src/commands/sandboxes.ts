import type * as yargs from "yargs";
import { TogetherSandbox } from "together-sandbox";
import type { SandboxRecord } from "together-sandbox";
import { runList, type ListArgs } from "./_list";
import { cell, humanBytes, renderDescribe } from "./_table";
import { fullCommand, parseEnv, runExec } from "./_exec";

function describeSandbox(s: SandboxRecord): {
  title: string;
  rows: [string, string][];
}[] {
  return [
    {
      title: "Identity",
      rows: [
        ["ID", cell(s.id)],
        ["Project", cell(s.project_id)],
        ["Ephemeral", cell(s.ephemeral)],
        ["Cluster", cell(s.cluster_name)],
      ],
    },
    {
      title: "Status",
      rows: [
        ["Status", cell(s.status)],
        ["Stop reason", cell(s.stop_reason)],
        ["Recovery", cell(s.recovery_status)],
      ],
    },
    {
      title: "Resources",
      rows: [
        ["Millicpu", cell(s.millicpu)],
        ["Memory", humanBytes(s.memory_bytes)],
        ["Disk", humanBytes(s.disk_bytes)],
        ["GPU", cell(s.gpu)],
      ],
    },
    {
      title: "Versions",
      rows: [
        ["Current", cell(s.current_version_number)],
        ["Next", cell(s.next_version_number)],
        ["Count", cell(s.version_count)],
      ],
    },
    {
      title: "Agent",
      rows: [
        ["Type", cell(s.agent_type)],
        ["Version", cell(s.agent_version)],
        ["URL", cell(s.agent_url)],
      ],
    },
    {
      title: "Lifecycle",
      rows: [
        ["Created", cell(s.created_at)],
        ["Started", cell(s.started_at)],
        ["Stopped", cell(s.stopped_at)],
        ["Updated", cell(s.updated_at)],
        ["Start type", cell(s.start_type)],
        ["Requested stop", cell(s.requested_stop_type)],
      ],
    },
  ];
}

export const listCommand: yargs.CommandModule<Record<string, never>, ListArgs> =
  {
    command: "list",
    describe: "List sandboxes.",
    builder: (yargs) =>
      yargs
        .option("limit", {
          type: "number",
          describe: "Maximum number of items per page (1–100)",
        })
        .option("cursor", {
          type: "string",
          describe: "Pagination cursor (a next_cursor from a previous page)",
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
            fetchPage: (params) => sdk.sandboxes.list(params),
            headers: ["ID", "STATUS", "CLUSTER", "CREATED"],
            toRow: (s) => [
              cell(s.id),
              cell(s.status),
              cell(s.cluster_name),
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
  id: string;
  output?: string;
}

export const getCommand: yargs.CommandModule<Record<string, never>, GetArgs> = {
  command: "get <id>",
  describe: "Show details for a single sandbox.",
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
        choices: ["text", "json"] as const,
        default: "text",
        describe: "Output format",
      }) as unknown as yargs.Argv<GetArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    try {
      const sandbox = await sdk.sandboxes.get(argv.id);
      if (argv.output === "json") {
        process.stdout.write(`${JSON.stringify(sandbox, null, 2)}\n`);
      } else {
        process.stdout.write(`${renderDescribe(describeSandbox(sandbox))}\n`);
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

// ─── Lifecycle commands (start / stop / hibernate) ──────────────────────────

interface IdArgs {
  id: string;
}

/** Build a `<verb> <id>` command that calls a lifecycle action and confirms. */
function lifecycleCommand(
  verb: string,
  describe: string,
  action: (sdk: TogetherSandbox, id: string) => Promise<unknown>,
  done: (id: string) => string,
  aliases: string[] = [],
): yargs.CommandModule<Record<string, never>, IdArgs> {
  return {
    command: `${verb} <id>`,
    aliases,
    describe,
    builder: (yargs) =>
      yargs.positional("id", {
        type: "string",
        describe: "Sandbox id",
        demandOption: true,
      }) as unknown as yargs.Argv<IdArgs>,
    handler: async (argv) => {
      try {
        const sdk = new TogetherSandbox();
        await action(sdk, argv.id);
        console.log(done(argv.id));
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
}

interface StartArgs {
  id: string;
  versionNumber?: number;
}

export const startCommand: yargs.CommandModule<Record<string, never>, StartArgs> =
  {
    command: "start <id>",
    describe: "Start an existing sandbox and wait until it is running.",
    builder: (yargs) =>
      yargs
        .positional("id", {
          type: "string",
          describe: "Sandbox id",
          demandOption: true,
        })
        .option("version-number", {
          type: "number",
          describe: "Version number to start (defaults to the current version)",
        }) as unknown as yargs.Argv<StartArgs>,
    handler: async (argv) => {
      try {
        const sdk = new TogetherSandbox();
        const sandbox = await sdk.sandboxes.start(
          argv.id,
          argv.versionNumber !== undefined
            ? { versionNumber: argv.versionNumber }
            : undefined,
        );
        console.log(`sandbox ${sandbox.id} started (running)`);
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

interface StartFromSnapshotArgs {
  ref: string;
  ephemeral?: boolean;
  millicpu?: number;
  memoryBytes?: number;
  diskBytes?: number;
}

export const startFromSnapshotCommand: yargs.CommandModule<
  Record<string, never>,
  StartFromSnapshotArgs
> = {
  command: "start-from-snapshot <ref>",
  describe:
    "Create a sandbox from a snapshot (by id or @alias) and start it.",
  builder: (yargs) =>
    yargs
      .positional("ref", {
        type: "string",
        describe: "Snapshot id, or @alias to resolve by alias",
        demandOption: true,
      })
      .option("ephemeral", {
        type: "boolean",
        describe: "Mark the created sandbox as ephemeral",
      })
      .option("millicpu", {
        type: "number",
        describe: "CPU allocation in millicpu",
      })
      .option("memory-bytes", {
        type: "number",
        describe: "Memory allocation in bytes",
      })
      .option("disk-bytes", {
        type: "number",
        describe: "Disk allocation in bytes",
      }) as unknown as yargs.Argv<StartFromSnapshotArgs>,
  handler: async (argv) => {
    try {
      const sdk = new TogetherSandbox();

      // A leading `@` selects the snapshot by alias (matches the API's
      // /snapshots/@{alias} convention); anything else is a raw snapshot id.
      const fromAlias = argv.ref.startsWith("@");
      const created = await sdk.sandboxes.create({
        snapshotId: fromAlias ? undefined : argv.ref,
        snapshotAlias: fromAlias ? argv.ref.slice(1) : undefined,
        ephemeral: argv.ephemeral,
        millicpu: argv.millicpu,
        memoryBytes: argv.memoryBytes,
        diskBytes: argv.diskBytes,
      });
      console.log(`created sandbox ${created.id}`);

      const sandbox = await sdk.sandboxes.start(created.id);
      console.log(`sandbox ${sandbox.id} started (running)`);
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

export const stopCommand = lifecycleCommand(
  "stop",
  "Stop (shut down) a sandbox.",
  (sdk, id) => sdk.sandboxes.shutdown(id),
  (id) => `sandbox ${id} stopped`,
  ["shutdown"],
);

export const hibernateCommand = lifecycleCommand(
  "hibernate",
  "Hibernate (suspend) a sandbox.",
  (sdk, id) => sdk.sandboxes.hibernate(id),
  (id) => `sandbox ${id} hibernated`,
);

interface RunArgs {
  ref: string;
  command: string[];
  interactive?: boolean;
  tty?: boolean;
  cwd?: string;
  env?: string[];
  user?: string;
  rm?: boolean;
  ephemeral?: boolean;
  millicpu?: number;
  memoryBytes?: number;
  diskBytes?: number;
}

export const runCommand: yargs.CommandModule<Record<string, never>, RunArgs> = {
  command: "run <ref> [command..]",
  describe:
    "Create a sandbox from a snapshot (id or @alias), start it, and run a " +
    "command in it (docker run-style).",
  builder: (yargs) =>
    yargs
      .positional("ref", {
        type: "string",
        describe: "Snapshot id, or @alias to resolve by alias",
        demandOption: true,
      })
      .positional("command", {
        type: "string",
        describe: "Command and arguments (use -- to separate from flags)",
        array: true,
        default: [] as string[],
      })
      .option("rm", {
        type: "boolean",
        default: false,
        describe: "Stop the sandbox when the command exits",
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
      .option("ephemeral", {
        type: "boolean",
        describe: "Mark the created sandbox as ephemeral",
      })
      .option("millicpu", { type: "number", describe: "CPU allocation in millicpu" })
      .option("memory-bytes", { type: "number", describe: "Memory allocation in bytes" })
      .option("disk-bytes", { type: "number", describe: "Disk allocation in bytes" })
      .check((argv) => {
        if (fullCommand(argv as Record<string, unknown>).length === 0)
          throw new Error("Provide a command to run, e.g. run @my-image -- ls -la");
        return true;
      }) as unknown as yargs.Argv<RunArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    let sandboxId: string | undefined;
    try {
      // A leading `@` selects the snapshot by alias; otherwise it's a raw id.
      const fromAlias = argv.ref.startsWith("@");
      const created = await sdk.sandboxes.create({
        snapshotId: fromAlias ? undefined : argv.ref,
        snapshotAlias: fromAlias ? argv.ref.slice(1) : undefined,
        ephemeral: argv.ephemeral,
        millicpu: argv.millicpu,
        memoryBytes: argv.memoryBytes,
        diskBytes: argv.diskBytes,
      });
      sandboxId = created.id;
      // Progress notices go to stderr so stdout stays clean for command output.
      process.stderr.write(`created sandbox ${sandboxId}\n`);

      const sandbox = await sdk.sandboxes.start(sandboxId);
      if (!sandbox.vmInfo.agentUrl || !sandbox.vmInfo.agentToken) {
        throw new Error(`sandbox ${sandboxId} has no agent connection details`);
      }

      const [cmd, ...args] = fullCommand(argv as Record<string, unknown>);
      const exitCode = await runExec(
        { agent: sandbox.vmInfo.agentUrl, token: sandbox.vmInfo.agentToken },
        { cmd, args, cwd: argv.cwd, env: parseEnv(argv.env), user: argv.user },
        { interactive: argv.interactive, tty: argv.tty },
      );

      if (argv.rm) {
        await sdk.sandboxes.shutdown(sandboxId);
        process.stderr.write(`stopped sandbox ${sandboxId}\n`);
      }
      process.exit(exitCode);
    } catch (error) {
      // Best-effort cleanup if --rm and the sandbox was created.
      if (argv.rm && sandboxId) {
        try {
          await sdk.sandboxes.shutdown(sandboxId);
          process.stderr.write(`stopped sandbox ${sandboxId}\n`);
        } catch {
          /* best effort */
        }
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

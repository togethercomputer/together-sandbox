import type * as yargs from "yargs";
import { TogetherSandbox } from "together-sandbox";
import type {
  SandboxInfo,
  SandboxStatus,
  TerminationSnapshotParams,
} from "together-sandbox";
import { runList, type ListArgs } from "./_list";
import {
  cell,
  formatAge,
  formatTagLines,
  formatTags,
  humanBytes,
  renderDescribe,
} from "./_table";
import {
  execTarget,
  fullCommand,
  parseEnv,
  parseKeyValues,
  runExec,
} from "./_exec";
import { examples } from "./_help";
import { withClientTag } from "../constants";

/** The statuses a sandbox can report, for `--status` validation. */
const SANDBOX_STATUSES = [
  "starting",
  "running",
  "terminating",
  "terminated",
  "failed_to_start",
  "recovering",
  "unrecovered",
] as const satisfies readonly SandboxStatus[];

/**
 * Summarise the termination policy. A sandbox created without one is
 * ephemeral: it takes no snapshot and is deleted when it terminates.
 */
function formatTerminationPolicy(s: SandboxInfo): string {
  const snapshot = s.terminationPolicy?.snapshot;
  if (!snapshot) return "<ephemeral>";
  const parts = ["filesystem"];
  if (snapshot.aliases?.length) parts.push(`aliases=${snapshot.aliases.join(",")}`);
  if (snapshot.ttl !== undefined) parts.push(`ttl=${snapshot.ttl}s`);
  return parts.join(" ");
}

function describeSandbox(s: SandboxInfo): {
  title: string;
  rows: [string, string][];
}[] {
  return [
    {
      title: "Identity",
      rows: [
        ["ID", cell(s.id)],
        ["Organization", cell(s.organizationId)],
        ["Project", cell(s.projectId)],
        ["Snapshot", cell(s.snapshotId)],
        ["Tags", formatTagLines(s.tags)],
      ],
    },
    {
      title: "Status",
      rows: [
        ["Status", cell(s.status)],
        ["Reason", cell(s.statusReason)],
      ],
    },
    {
      title: "Resources",
      rows: [
        ["CPU", cell(s.cpu)],
        ["Memory", humanBytes(s.memoryBytes)],
      ],
    },
    {
      title: "Termination",
      rows: [
        ["TTL", s.ttl !== null && s.ttl !== undefined ? `${s.ttl}s` : cell(undefined)],
        ["Policy", formatTerminationPolicy(s)],
      ],
    },
    {
      title: "Agent",
      rows: [
        ["Version", cell(s.agent?.version)],
        ["URL", cell(s.agent?.url)],
      ],
    },
    {
      title: "Lifecycle",
      rows: [
        ["Created", cell(s.createdAt)],
        ["Started", cell(s.startedAt)],
        ["Terminated", cell(s.terminatedAt)],
        ["Resized", cell(s.resizedAt)],
        ["Recovered", cell(s.recoveryAt)],
        ["Updated", cell(s.updatedAt)],
      ],
    },
  ];
}

interface SandboxListArgs extends ListArgs {
  status?: string[];
  tag?: string[];
  all?: boolean;
}

/**
 * Pick the status filter. An unfiltered list is dominated by terminated
 * sandboxes, which are rarely what you are looking for, so default to running
 * ones — as `docker ps` does. `--status` replaces the default and `--all` drops
 * it; `--tag` narrows within it rather than opting out.
 */
function listStatuses(argv: SandboxListArgs): SandboxStatus[] | undefined {
  if (argv.all) return undefined;
  if (argv.status?.length) return argv.status as SandboxStatus[];
  return ["running"];
}

export const listCommand: yargs.CommandModule<
  Record<string, never>,
  SandboxListArgs
> = {
  command: "list",
  describe: "List running sandboxes (use --all or --status for the rest).",
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
      .option("status", {
        type: "string",
        array: true,
        choices: SANDBOX_STATUSES,
        describe: "Only show sandboxes in this status (repeatable)",
      })
      .option("tag", {
        type: "string",
        array: true,
        describe:
          "Only show sandboxes carrying this tag, KEY=VALUE (repeatable; all must match)",
      })
      .option("all", {
        alias: "a",
        type: "boolean",
        // No `default`: yargs' `conflicts` treats a defaulted key as present,
        // which would make --status collide with an --all nobody passed.
        describe: "Show sandboxes in every status, not just running ones",
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
      .conflicts("all", "status")
      .epilogue(
        examples(
          [
            {
              describe: "Running sandboxes only (the default)",
              command: "$0 sandboxes list",
            },
            {
              describe: "Every sandbox, including terminated ones",
              command: "$0 sandboxes list --all",
            },
            {
              describe: "Only sandboxes that are up or coming up",
              command: "$0 sandboxes list --status running --status starting",
            },
            {
              describe: "Running sandboxes carrying both tags",
              command: "$0 sandboxes list --tag env=prod --tag team=core",
            },
            {
              describe: "Tagged sandboxes in any status",
              command: "$0 sandboxes list --all --tag env=prod",
            },
            {
              describe:
                "Fetch one specific page (the next cursor is printed on stderr)",
              command: "$0 sandboxes list --limit 50 --cursor <cursor>",
            },
            {
              describe: "Machine-readable single page: { data, nextCursor }",
              command: "$0 sandboxes list --ci -o json",
            },
          ],
          "By default only running sandboxes are listed. --status replaces that default\n" +
            "and --all drops it; --tag narrows within it, so combine --tag with --all to\n" +
            "search every status.",
        ),
      ) as unknown as yargs.Argv<SandboxListArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    try {
      const statuses = listStatuses(argv);
      const tags = parseKeyValues(argv.tag, "--tag");
      await runList(
        {
          fetchPage: (params) =>
            sdk.sandboxes.list({ ...params, statuses, tags }),
          // TAGS is last: it is the only unbounded-width column, and
          // `renderTable` truncates the final column to fit the terminal.
          headers: ["ID", "STATUS", "REASON", "CPU", "AGE", "TAGS"],
          toRow: (s) => [
            cell(s.id),
            cell(s.status),
            cell(s.statusReason),
            cell(s.cpu),
            formatAge(s.createdAt),
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
      })
      .epilogue(
        examples([
          {
            describe: "Show status, resources, termination policy and agent",
            command: "$0 sandboxes get <sandbox-id>",
          },
          {
            describe: "Machine-readable output",
            command: "$0 sandboxes get <sandbox-id> -o json",
          },
        ]),
      ) as unknown as yargs.Argv<GetArgs>,

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

// ─── Creation ────────────────────────────────────────────────────────────────

/** Options shared by `create` and `run` for shaping the new sandbox. */
interface CreateOptions {
  cpu?: number;
  memoryBytes?: number;
  ttl?: number;
  tag?: string[];
  snapshotOnTerminate?: boolean;
  snapshotAlias?: string[];
  snapshotTtl?: number;
}

function createOptionsBuilder<T>(yargs: yargs.Argv<T>) {
  return yargs
    .option("cpu", {
      type: "number",
      describe: "CPU allocation in cores (0.1–16, default 1)",
    })
    .option("memory-bytes", {
      type: "number",
      describe: "Memory allocation in bytes (default 2 GiB)",
    })
    .option("ttl", {
      type: "number",
      describe:
        "Seconds after creation before the sandbox is automatically terminated",
    })
    .option("tag", {
      type: "string",
      array: true,
      describe: "Tag the sandbox, KEY=VALUE (repeatable)",
    })
    .option("snapshot-on-terminate", {
      type: "boolean",
      default: false,
      describe:
        "Snapshot the sandbox when it terminates. Without this the sandbox is " +
        "ephemeral: no snapshot is taken and it is deleted on termination",
    })
    .option("snapshot-alias", {
      type: "string",
      array: true,
      describe:
        "With --snapshot-on-terminate, alias to apply to the produced snapshot " +
        "(repeatable)",
    })
    .option("snapshot-ttl", {
      type: "number",
      describe:
        "With --snapshot-on-terminate, seconds before the produced snapshot expires",
    });
}

/**
 * Build the `create` params. A sandbox is ephemeral unless a termination
 * policy is supplied, so `--snapshot-on-terminate` is what turns the snapshot
 * on — the other `--snapshot-*` flags only shape it.
 */
function buildCreateParams(argv: CreateOptions, ref: string) {
  // A leading `@` selects the snapshot by alias (matches the API's
  // /snapshots/@{alias} convention); anything else is a raw snapshot id.
  const fromAlias = ref.startsWith("@");
  return {
    snapshotId: fromAlias ? undefined : ref,
    snapshotAlias: fromAlias ? ref.slice(1) : undefined,
    cpu: argv.cpu,
    memoryBytes: argv.memoryBytes,
    ttl: argv.ttl,
    tags: withClientTag(parseKeyValues(argv.tag, "--tag")),
    terminationPolicy: argv.snapshotOnTerminate
      ? {
          snapshot: {
            aliases: argv.snapshotAlias,
            ttl: argv.snapshotTtl,
          },
        }
      : undefined,
  };
}

interface CreateArgs extends CreateOptions {
  ref: string;
}

export const createCommand: yargs.CommandModule<
  Record<string, never>,
  CreateArgs
> = {
  command: "create <ref>",
  describe:
    "Create a sandbox from a snapshot (by id or @alias) and wait until it is " +
    "running.",
  builder: (yargs) =>
    createOptionsBuilder(
      yargs.positional("ref", {
        type: "string",
        describe: "Snapshot id, or @alias to resolve by alias",
        demandOption: true,
      }),
    )
      .epilogue(
        examples([
          {
            describe: "Ephemeral sandbox from a snapshot id, default resources",
            command: "$0 sandboxes create <snapshot-id>",
          },
          {
            describe: "From an alias, with 2 vCPUs",
            command: "$0 sandboxes create @my-app@v1 --cpu 2",
          },
          {
            describe: "Auto-terminate after an hour, tagged env=dev",
            command: "$0 sandboxes create @my-app@v1 --ttl 3600 --tag env=dev",
          },
          {
            describe: "Snapshot on teardown, aliased my-app@v2",
            command:
              "$0 sandboxes create @my-app@v1 --snapshot-on-terminate --snapshot-alias my-app@v2",
          },
        ]),
      ) as unknown as yargs.Argv<CreateArgs>,

  handler: async (argv) => {
    try {
      const sdk = new TogetherSandbox();
      const sandbox = await sdk.sandboxes.create(
        buildCreateParams(argv, argv.ref),
      );
      console.log(`created sandbox ${sandbox.id} (running)`);
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

// ─── Termination ─────────────────────────────────────────────────────────────

interface TerminateArgs {
  id: string;
  ephemeral?: boolean;
  snapshotAlias?: string[];
  snapshotTtl?: number;
  snapshotTag?: string[];
}

/**
 * Resolve the `snapshot` override for a teardown. The three states are
 * distinct on the wire: `undefined` keeps the sandbox's stored termination
 * policy, `null` makes this teardown ephemeral, and an object overrides it.
 */
function terminateSnapshotOverride(
  argv: TerminateArgs,
): TerminationSnapshotParams | null | undefined {
  if (argv.ephemeral) return null;
  const overridden =
    argv.snapshotAlias !== undefined ||
    argv.snapshotTtl !== undefined ||
    argv.snapshotTag !== undefined;
  if (!overridden) return undefined;
  return {
    aliases: argv.snapshotAlias,
    ttl: argv.snapshotTtl,
    tags: parseKeyValues(argv.snapshotTag, "--snapshot-tag"),
  };
}

export const terminateCommand: yargs.CommandModule<
  Record<string, never>,
  TerminateArgs
> = {
  command: "terminate <id>",
  describe:
    "Terminate a sandbox and wait until it is torn down. Terminating is " +
    "permanent — create a new sandbox from the produced snapshot to continue.",
  builder: (yargs) =>
    yargs
      .positional("id", {
        type: "string",
        describe: "Sandbox id",
        demandOption: true,
      })
      .option("ephemeral", {
        type: "boolean",
        describe: "Take no snapshot at all, overriding the stored policy",
      })
      .option("snapshot-alias", {
        type: "string",
        array: true,
        describe: "Alias to apply to the produced snapshot (repeatable)",
      })
      .option("snapshot-ttl", {
        type: "number",
        describe: "Seconds before the produced snapshot expires",
      })
      .option("snapshot-tag", {
        type: "string",
        array: true,
        describe: "Tag the produced snapshot, KEY=VALUE (repeatable)",
      })
      .conflicts("ephemeral", ["snapshot-alias", "snapshot-ttl", "snapshot-tag"])
      .epilogue(
        examples(
          [
            {
              describe:
                "Use the termination policy the sandbox was created with",
              command: "$0 sandboxes terminate <sandbox-id>",
            },
            {
              describe: "Throw the sandbox away, taking no snapshot",
              command: "$0 sandboxes terminate <sandbox-id> --ephemeral",
            },
            {
              describe: "Snapshot on teardown under a known alias",
              command:
                "$0 sandboxes terminate <sandbox-id> --snapshot-alias my-app@paused",
            },
          ],
          "With no snapshot flags, the sandbox's stored termination policy applies.",
          "The produced snapshot is always aliased `sandbox:<sandbox-id>`, so you can\n" +
            "resume later with: $0 sandboxes create @sandbox:<sandbox-id>",
        ),
      ) as unknown as yargs.Argv<TerminateArgs>,

  handler: async (argv) => {
    try {
      const sdk = new TogetherSandbox();
      const snapshot = terminateSnapshotOverride(argv);
      await sdk.sandboxes.terminate(
        argv.id,
        snapshot === undefined ? {} : { snapshot },
      );
      console.log(`sandbox ${argv.id} terminated`);
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

// ─── Run ─────────────────────────────────────────────────────────────────────

interface RunArgs extends CreateOptions {
  ref: string;
  command: string[];
  interactive?: boolean;
  tty?: boolean;
  cwd?: string;
  env?: string[];
  user?: string;
  rm?: boolean;
}

export const runCommand: yargs.CommandModule<Record<string, never>, RunArgs> = {
  command: "run <ref> [command..]",
  describe:
    "Create a sandbox from a snapshot (id or @alias) and run a command in it " +
    "(docker run-style).",
  builder: (yargs) =>
    createOptionsBuilder(
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
          describe: "Terminate the sandbox when the command exits",
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
        }),
    )
      .epilogue(
        examples(
          [
            {
              describe: "One-shot command",
              command: "$0 sandboxes run @my-app@v1 -- ls -la",
            },
            {
              describe: "Run tests and tear the sandbox down afterwards",
              command: "$0 sandboxes run @my-app@v1 --rm -- npm test",
            },
            {
              describe: "Interactive shell in a throwaway sandbox",
              command: "$0 sandboxes run @my-app@v1 -it --rm -- bash",
            },
            {
              describe: "Size the sandbox and shape the command's environment",
              command:
                "$0 sandboxes run @my-app@v1 --cpu 4 --env NODE_ENV=test --cwd /app -- npm run bench",
            },
          ],
          "Accepts every option of `$0 sandboxes create` and `$0 sandboxes exec`.",
          "Progress notices go to stderr, so stdout carries only the command's output.\n" +
            "The CLI exits with the remote command's exit code.",
        ),
      )
      .check((argv) => {
        if (fullCommand(argv as Record<string, unknown>).length === 0)
          throw new Error(
            "Provide a command to run, e.g. run @my-image -- ls -la",
          );
        return true;
      }) as unknown as yargs.Argv<RunArgs>,

  handler: async (argv) => {
    const sdk = new TogetherSandbox();
    let sandboxId: string | undefined;
    try {
      // `create` autostarts and waits, so the returned sandbox is running.
      const sandbox = await sdk.sandboxes.create(
        buildCreateParams(argv, argv.ref),
      );
      sandboxId = sandbox.id;
      // Progress notices go to stderr so stdout stays clean for command output.
      process.stderr.write(`created sandbox ${sandboxId}\n`);

      const [cmd, ...args] = fullCommand(argv as Record<string, unknown>);
      const exitCode = await runExec(
        execTarget(sandbox.vmInfo),
        { cmd, args, cwd: argv.cwd, env: parseEnv(argv.env), user: argv.user },
        { interactive: argv.interactive, tty: argv.tty },
      );

      if (argv.rm) {
        await sdk.sandboxes.terminate(sandboxId);
        process.stderr.write(`terminated sandbox ${sandboxId}\n`);
      }
      process.exit(exitCode);
    } catch (error) {
      // Best-effort cleanup if --rm and the sandbox was created.
      if (argv.rm && sandboxId) {
        try {
          await sdk.sandboxes.terminate(sandboxId);
          process.stderr.write(`terminated sandbox ${sandboxId}\n`);
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

import yargs from "yargs";
import { hideBin } from "yargs/helpers";

import { examples } from "./commands/_help";

import {
  createCommand,
  listCommand as snapshotsListCommand,
  getCommand as snapshotsGetCommand,
} from "./commands/snapshots";
import {
  listCommand as sandboxesListCommand,
  getCommand as sandboxesGetCommand,
  createCommand as sandboxesCreateCommand,
  terminateCommand as sandboxesTerminateCommand,
  runCommand as sandboxesRunCommand,
} from "./commands/sandboxes";
import {
  createCommand as execsCreateCommand,
  runCommand as execsRunCommand,
  lsCommand as execsLsCommand,
  logsCommand as execsLogsCommand,
} from "./commands/execs";

let snapshotsYargs: ReturnType<typeof yargs>;
let sandboxesYargs: ReturnType<typeof yargs>;
let execsYargs: ReturnType<typeof yargs>;

const argv = hideBin(process.argv);

const ROOT_EPILOGUE = examples(
  [
    {
      describe: "Build a snapshot from the current directory",
      command: "$0 snapshots create --context . --alias my-app@v1",
    },
    {
      describe: "Run a command in a throwaway sandbox",
      command: "$0 sandboxes run @my-app@v1 --rm -- npm test",
    },
    {
      describe: "Create a long-lived sandbox",
      command: "$0 sandboxes create @my-app@v1",
    },
    {
      describe: "Open a shell in a running sandbox",
      command: "$0 sandbox exec run <sandbox-id> -it -- bash",
    },
    {
      describe: "See what is running",
      command: "$0 sandboxes list",
    },
  ],
  "Run `$0 <command> --help` for the options and examples of any command.",
);

/**
 * Print help and exit non-zero.
 *
 * `showHelp()` defaults to `console.error`, which paints the whole help block
 * in stderr colouring and reads like a crash. Naming a command group without an
 * action is not a malformed command, so the help goes to stdout — as git, npm,
 * gh and kubectl all do — while the exit code stays non-zero because nothing
 * ran, which is what a script needs to see.
 */
function showHelpAndExit(instance: ReturnType<typeof yargs>): void {
  instance.showHelp("log");
  process.exit(1);
}

const cli = yargs(argv)
  .usage("together-sandbox CLI - Manage your Together Sandbox projects")
  .scriptName("together-sandbox")
  .strict()
  // Keep args after `--` available (in argv["--"]) so `exec`/`run` can pass a
  // command through without yargs swallowing it.
  .parserConfiguration({ "populate--": true })
  // Default yargs wraps at 80, which breaks the example commands mid-token and
  // makes them non-copy-pasteable. Use the terminal width up to 120.
  .wrap(Math.min(process.stdout.columns || 120, 120))
  .recommendCommands()
  .command({
    command: "snapshots",
    aliases: ["snapshot"],
    describe: "Manage snapshots",
    builder: (yargs) => {
      snapshotsYargs = yargs
        .recommendCommands()
        .command(createCommand)
        .command(snapshotsListCommand)
        .command(snapshotsGetCommand);
      return snapshotsYargs;
    },
    handler: () => {
      showHelpAndExit(snapshotsYargs);
    },
  })
  .command({
    command: "sandboxes",
    aliases: ["sandbox"],
    describe: "Manage sandboxes",
    builder: (yargs) => {
      sandboxesYargs = yargs
        .recommendCommands()
        .command(sandboxesListCommand)
        .command(sandboxesGetCommand)
        .command(sandboxesCreateCommand)
        .command(sandboxesTerminateCommand)
        .command(sandboxesRunCommand)
        .command({
          command: "exec",
          aliases: ["execs"],
          describe: "Run and inspect commands inside a sandbox",
          builder: (yargs) => {
            execsYargs = yargs
              .recommendCommands()
              .command(execsCreateCommand)
              .command(execsRunCommand)
              .command(execsLsCommand)
              .command(execsLogsCommand);
            return execsYargs;
          },
          handler: () => {
            showHelpAndExit(execsYargs);
          },
        });
      return sandboxesYargs;
    },
    handler: () => {
      showHelpAndExit(sandboxesYargs);
    },
  });

// yargs shares one instance across the whole command tree, so an epilogue set
// here would override the per-command ones the builders install. Only attach
// the root examples when no subcommand was named.
if (!argv.some((arg) => !arg.startsWith("-"))) {
  cli.epilogue(ROOT_EPILOGUE);
}

cli.parse();

// A bare invocation parses cleanly (there is nothing to validate), so handle it
// here rather than via `demandCommand`, whose failure path writes to stderr.
// `--help` / `--version` exit inside `parse()` and never reach this.
if (argv.length === 0) {
  showHelpAndExit(cli);
}

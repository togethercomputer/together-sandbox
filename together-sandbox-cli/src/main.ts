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
import { execCommand as sandboxesExecCommand } from "./commands/exec";
import {
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
      command: "$0 sandboxes exec <sandbox-id> -it -- bash",
    },
    {
      describe: "See what is running",
      command: "$0 sandboxes list",
    },
  ],
  "Run `$0 <command> --help` for the options and examples of any command.",
);

const cli = yargs(argv)
  .usage("together-sandbox CLI - Manage your Together Sandbox projects")
  .demandCommand(1, "Usage: together-sandbox <command> [options]")
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
      snapshotsYargs.showHelp();
    },
  })
  .command({
    command: "sandboxes",
    describe: "Manage sandboxes",
    builder: (yargs) => {
      sandboxesYargs = yargs
        .recommendCommands()
        .command(sandboxesListCommand)
        .command(sandboxesGetCommand)
        .command(sandboxesCreateCommand)
        .command(sandboxesTerminateCommand)
        .command(sandboxesExecCommand)
        .command(sandboxesRunCommand)
        .command({
          command: "execs",
          describe: "Inspect execs running in a sandbox",
          builder: (yargs) => {
            execsYargs = yargs
              .recommendCommands()
              .command(execsLsCommand)
              .command(execsLogsCommand);
            return execsYargs;
          },
          handler: () => {
            execsYargs.showHelp();
          },
        });
      return sandboxesYargs;
    },
    handler: () => {
      sandboxesYargs.showHelp();
    },
  });

// yargs shares one instance across the whole command tree, so an epilogue set
// here would override the per-command ones the builders install. Only attach
// the root examples when no subcommand was named.
if (!argv.some((arg) => !arg.startsWith("-"))) {
  cli.epilogue(ROOT_EPILOGUE);
}

cli.parse();

import yargs from "yargs";
import { hideBin } from "yargs/helpers";

import {
  createCommand,
  listCommand as snapshotsListCommand,
  getCommand as snapshotsGetCommand,
} from "./commands/snapshots";
import {
  listCommand as sandboxesListCommand,
  getCommand as sandboxesGetCommand,
  startCommand as sandboxesStartCommand,
  startFromSnapshotCommand as sandboxesStartFromSnapshotCommand,
  stopCommand as sandboxesStopCommand,
  hibernateCommand as sandboxesHibernateCommand,
  runCommand as sandboxesRunCommand,
} from "./commands/sandboxes";
import { execCommand as sandboxesExecCommand } from "./commands/exec";

let snapshotsYargs: ReturnType<typeof yargs>;
let sandboxesYargs: ReturnType<typeof yargs>;

yargs(hideBin(process.argv))
  .usage("together-sandbox CLI - Manage your Together Sandbox projects")
  .demandCommand(1, "Usage: together-sandbox <command> [options]")
  .scriptName("together-sandbox")
  .strict()
  // Keep args after `--` available (in argv["--"]) so `exec`/`run` can pass a
  // command through without yargs swallowing it.
  .parserConfiguration({ "populate--": true })
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
        .command(sandboxesStartCommand)
        .command(sandboxesStartFromSnapshotCommand)
        .command(sandboxesStopCommand)
        .command(sandboxesHibernateCommand)
        .command(sandboxesExecCommand)
        .command(sandboxesRunCommand);
      return sandboxesYargs;
    },
    handler: () => {
      sandboxesYargs.showHelp();
    },
  })
  .parse();

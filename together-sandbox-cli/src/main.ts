import yargs from "yargs";
import { hideBin } from "yargs/helpers";

import { createCommand } from "./commands/snapshots";

let snapshotsYargs: ReturnType<typeof yargs>;

yargs(hideBin(process.argv))
  .usage("together-sandbox CLI - Manage your Together Sandbox projects")
  .demandCommand(1, "Usage: together-sandbox <command> [options]")
  .scriptName("together-sandbox")
  .strict()
  .recommendCommands()
  .command({
    command: "snapshots",
    describe: "Manage snapshots",
    builder: (yargs) => {
      snapshotsYargs = yargs.recommendCommands().command(createCommand);
      return snapshotsYargs;
    },
    handler: () => {
      snapshotsYargs.showHelp();
    },
  })
  .parse();

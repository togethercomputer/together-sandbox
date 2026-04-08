import yargs from "yargs";
import { hideBin } from "yargs/helpers";

import { buildCommand } from "./commands/build";
import { sandboxesCommand } from "./commands/sandbox";
import { hostTokensCommand } from "./commands/hostTokens";

yargs(hideBin(process.argv))
  .usage("together-sandbox CLI - Manage your Together Sandbox projects")
  .demandCommand(1, "Usage: together-sandbox <command> [options]")
  .scriptName("together-sandbox")
  .strict()
  .recommendCommands()
  .command(buildCommand)
  .command(sandboxesCommand)
  .command(hostTokensCommand)
  .parse();

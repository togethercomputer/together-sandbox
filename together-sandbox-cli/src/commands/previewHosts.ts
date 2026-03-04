import type * as yargs from "yargs";
import { api } from "@together-sandbox/sdk";
import { createClient, handleResponse } from "../utils/api";
import { getInferredApiKey } from "../utils/constants";

function getClient() {
  return createClient(getInferredApiKey());
}

export const previewHostsCommand: yargs.CommandModule = {
  command: "preview-hosts",
  describe:
    "Manage preview hosts that should be able to access the Preview API",
  builder: (yargs) => {
    return yargs
      .command({
        command: "list",
        describe: "List current preview hosts",
        handler: async () => {
          const client = getClient();
          const response = handleResponse(
            await api.previewHostList({ client }),
            "Failed to list preview hosts"
          );
          const hosts = response.preview_hosts.map(({ host }) => host);
          if (hosts.length) {
            console.log(hosts.join("\n"));
          } else {
            console.log("No preview hosts found");
          }
        },
      })
      .command({
        command: "add <host>",
        describe: "Add a preview host",
        builder: (yargs) =>
          yargs.positional("host", {
            describe: "Host to add",
            type: "string",
            demandOption: true,
          }),
        handler: async (argv) => {
          const client = getClient();
          const response = handleResponse(
            await api.previewHostList({ client }),
            "Failed to list preview hosts"
          );
          let hosts = response.preview_hosts.map(({ host }) => host);
          const hostToAdd = (argv.host as string).trim();
          if (hosts.includes(hostToAdd)) {
            console.log(`Host already exists: ${hostToAdd}`);
            return;
          }
          hosts.push(hostToAdd);
          handleResponse(
            await api.previewHostUpdate({ client, body: { hosts } }),
            "Failed to update preview hosts"
          );
          console.log(`Added preview host: ${hostToAdd}`);
        },
      })
      .command({
        command: "remove <host>",
        describe: "Remove a preview host",
        builder: (yargs) =>
          yargs.positional("host", {
            describe: "Host to remove",
            type: "string",
            demandOption: true,
          }),
        handler: async (argv) => {
          const client = getClient();
          const response = handleResponse(
            await api.previewHostList({ client }),
            "Failed to list preview hosts"
          );
          let hosts = response.preview_hosts.map(({ host }) => host);
          const hostToRemove = (argv.host as string).trim();
          if (!hosts.includes(hostToRemove)) {
            console.log(`Host not found: ${hostToRemove}`);
            return;
          }
          hosts = hosts.filter((h) => h !== hostToRemove);
          handleResponse(
            await api.previewHostUpdate({ client, body: { hosts } }),
            "Failed to update preview hosts"
          );
          console.log(`Removed preview host: ${hostToRemove}`);
        },
      })
      .command({
        command: "clear",
        describe: "Clear all preview hosts",
        handler: async () => {
          const client = getClient();
          const response = handleResponse(
            await api.previewHostList({ client }),
            "Failed to list preview hosts"
          );
          const hosts = response.preview_hosts.map(({ host }) => host);
          if (hosts.length === 0) {
            console.log("Preview host list is already empty.");
            return;
          }
          handleResponse(
            await api.previewHostUpdate({ client, body: { hosts: [] } }),
            "Failed to update preview hosts"
          );
          console.log("Cleared all preview hosts.");
        },
      });
  },
  handler: () => {},
};

import ora from "ora";
import { api } from "@together-sandbox/sdk";
import { createClient, handleResponse } from "../../utils/api";
import { getInferredApiKey } from "../../utils/constants";

export async function forkSandbox(sandboxId: string) {
  const client = createClient(getInferredApiKey());

  const spinner = ora("Forking sandbox...").start();
  const sandbox = handleResponse(
    await api.sandboxFork({ client, path: { id: sandboxId } }),
    `Failed to fork sandbox ${sandboxId}`
  );
  spinner.succeed("Sandbox forked successfully");

  // eslint-disable-next-line no-console
  console.log(sandbox.id);
}

import ora from "ora";

import { API, getInferredApiKey } from "@together-sandbox/sdk";

export async function forkSandbox(sandboxId: string) {
  const api = new API({ apiKey: getInferredApiKey() });

  const spinner = ora("Forking sandbox...").start();
  const sandbox = await api.forkSandbox(sandboxId);
  spinner.succeed("Sandbox forked successfully");

  // eslint-disable-next-line no-console
  console.log(sandbox.id);
}

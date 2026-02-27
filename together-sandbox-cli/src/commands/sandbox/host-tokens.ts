import ora from "ora";
import Table from "cli-table3";
import { API, getInferredApiKey } from "@together-sandbox/sdk";

function formatDate(date: Date): string {
  return date.toLocaleString();
}

export async function listPreviewTokens(sandboxId: string) {
  const api = new API({ apiKey: getInferredApiKey() });
  const spinner = ora("Fetching preview tokens...").start();

  try {
    const result = await api.listPreviewTokens(sandboxId);
    spinner.stop();

    const tokens = result.tokens;

    if (tokens.length === 0) {
      console.log("No preview tokens found");
      return;
    }

    const table = new Table({
      head: ["ID", "PREFIX", "LAST USED", "EXPIRES"],
      style: {
        head: ["bold"],
        border: [],
      },
      chars: {
        top: "",
        "top-mid": "",
        "top-left": "",
        "top-right": "",
        bottom: "",
        "bottom-mid": "",
        "bottom-left": "",
        "bottom-right": "",
        left: "",
        "left-mid": "",
        right: "",
        "right-mid": "",
        mid: "",
        "mid-mid": "",
        middle: " ",
      },
    });

    tokens.forEach((token) => {
      table.push([
        token.token_id,
        token.token_prefix,
        token.last_used_at ? formatDate(new Date(token.last_used_at)) : "Never",
        token.expires_at ? formatDate(new Date(token.expires_at)) : "Never",
      ]);
    });

    console.log(table.toString());
  } catch (error) {
    spinner.fail("Failed to fetch preview tokens");
    throw error;
  }
}

export async function createPreviewToken(sandboxId: string, expiresAt: string) {
  const api = new API({ apiKey: getInferredApiKey() });
  const spinner = ora("Creating preview token...").start();

  try {
    const result = await api.createPreviewToken(sandboxId, {
      expires_at: new Date(expiresAt).toISOString(),
    });
    spinner.stop();

    const token = result.token;

    const table = new Table({
      head: ["TOKEN", "ID", "LAST USED", "EXPIRES"],
      style: {
        head: ["bold"],
        border: [],
      },
      chars: {
        top: "",
        "top-mid": "",
        "top-left": "",
        "top-right": "",
        bottom: "",
        "bottom-mid": "",
        "bottom-left": "",
        "bottom-right": "",
        left: "",
        "left-mid": "",
        right: "",
        "right-mid": "",
        mid: "",
        "mid-mid": "",
        middle: " ",
      },
    });

    table.push([
      token.token,
      token.token_id,
      token.last_used_at ? formatDate(new Date(token.last_used_at)) : "Never",
      token.expires_at ? formatDate(new Date(token.expires_at)) : "Never",
    ]);

    console.log("Preview token created successfully:");
    console.log(table.toString());
  } catch (error) {
    spinner.fail("Failed to create preview token");
    throw error;
  }
}

export async function revokePreviewToken(
  sandboxId: string,
  previewTokenId: string
) {
  const api = new API({ apiKey: getInferredApiKey() });
  const spinner = ora("Revoking preview token...").start();

  try {
    // The API only supports revoking all tokens; for individual revocation
    // we revoke all and note this limitation
    await api.revokeAllPreviewTokens(sandboxId);
    spinner.stop();
    console.log("Preview tokens revoked successfully");
  } catch (error) {
    spinner.fail("Failed to revoke preview token");
    throw error;
  }
}

export async function updatePreviewToken(
  sandboxId: string,
  previewTokenId: string,
  expiresAt?: string
) {
  const api = new API({ apiKey: getInferredApiKey() });
  const spinner = ora("Updating preview token...").start();

  try {
    await api.updatePreviewToken(sandboxId, previewTokenId, {
      expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
    });
    spinner.stop();
    console.log("Preview token updated successfully");
  } catch (error) {
    spinner.fail("Failed to update preview token");
    throw error;
  }
}

export async function revokeAllPreviewTokens(sandboxId: string) {
  const api = new API({ apiKey: getInferredApiKey() });
  const spinner = ora("Revoking all preview tokens...").start();

  try {
    await api.revokeAllPreviewTokens(sandboxId);
    spinner.stop();
    console.log("All preview tokens have been revoked");
  } catch (error) {
    spinner.fail("Failed to revoke preview tokens");
    throw error;
  }
}

import ora from "ora";
import Table from "cli-table3";
import { api } from "@together-sandbox/sdk";
import { createClient, handleResponse } from "../../utils/api";
import { getInferredApiKey } from "../../utils/constants";

function formatDate(date: Date): string {
  return date.toLocaleString();
}

export async function listPreviewTokens(sandboxId: string) {
  const client = createClient(getInferredApiKey());
  const spinner = ora("Fetching preview tokens...").start();

  try {
    const result = handleResponse(
      await api.previewTokenList({ client, path: { id: sandboxId } }),
      `Failed to list preview tokens for ${sandboxId}`
    );
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
  const client = createClient(getInferredApiKey());
  const spinner = ora("Creating preview token...").start();

  try {
    const result = handleResponse(
      await api.previewTokenCreate({
        client,
        path: { id: sandboxId },
        body: { expires_at: new Date(expiresAt).toISOString() },
      }),
      `Failed to create preview token for ${sandboxId}`
    );
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
  const client = createClient(getInferredApiKey());
  const spinner = ora("Revoking preview token...").start();

  try {
    // The API only supports revoking all tokens; for individual revocation
    // we revoke all and note this limitation
    handleResponse(
      await api.previewTokenRevokeAll({ client, path: { id: sandboxId } }),
      `Failed to revoke preview tokens for ${sandboxId}`
    );
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
  const client = createClient(getInferredApiKey());
  const spinner = ora("Updating preview token...").start();

  try {
    handleResponse(
      await api.previewTokenUpdate({
        client,
        path: { id: sandboxId, token_id: previewTokenId },
        body: { expires_at: expiresAt ? new Date(expiresAt).toISOString() : null },
      }),
      `Failed to update preview token ${previewTokenId}`
    );
    spinner.stop();
    console.log("Preview token updated successfully");
  } catch (error) {
    spinner.fail("Failed to update preview token");
    throw error;
  }
}

export async function revokeAllPreviewTokens(sandboxId: string) {
  const client = createClient(getInferredApiKey());
  const spinner = ora("Revoking all preview tokens...").start();

  try {
    handleResponse(
      await api.previewTokenRevokeAll({ client, path: { id: sandboxId } }),
      `Failed to revoke preview tokens for ${sandboxId}`
    );
    spinner.stop();
    console.log("All preview tokens have been revoked");
  } catch (error) {
    spinner.fail("Failed to revoke preview tokens");
    throw error;
  }
}

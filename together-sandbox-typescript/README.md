# @together-sandbox/sdk

TypeScript SDK for the Together Sandbox API.

## Installation

```bash
npm install @together-sandbox/sdk
```

## Usage

The SDK exposes two clients:

- **`api`** — manages sandboxes (create, fork, start, shutdown, etc.)
- **`sandbox`** — interacts with a running sandbox via its Pint URL (filesystem, terminals, processes, etc.)

```ts
import {
  api,
  sandbox,
  createApiClient,
  createApiConfig,
  createSandboxClient,
  createSandboxConfig,
} from "@together-sandbox/sdk";

// Create the management API client
const client = createApiClient(
  createApiConfig({
    baseUrl: "https://api.codesandbox.io",
    headers: { Authorization: `Bearer ${process.env.TOGETHER_API_KEY}` },
  }),
);

// Fork a sandbox from a template
const forkResult = await api.sandboxFork({
  client,
  path: { id: "your-template-id" },
  body: { privacy: 0, private_preview: false },
});

const sandboxId = forkResult.data.data.id;

// Start the sandbox
const startResult = await api.vmStart({
  client,
  path: { id: sandboxId },
});

const { pint_url, pint_token } = startResult.data.data;

// Connect to the running sandbox
const sandboxClient = createSandboxClient(
  createSandboxConfig({
    baseUrl: pint_url,
    headers: { Authorization: `Bearer ${pint_token}` },
  }),
);

// Interact with the sandbox filesystem
const dirResult = await sandbox.listDirectory({
  client: sandboxClient,
  path: { path: "/" },
});

for (const entry of dirResult.data.files) {
  console.log(entry.isDir ? "[dir] " : "[file]", entry.name);
}

// Shut down the sandbox when done
await api.vmShutdown({ client, path: { id: sandboxId } });
```

## Environment Variables

| Variable | Description |
|---|---|
| `TOGETHER_API_KEY` | Your Together / CodeSandbox API key |
| `TOGETHER_BASE_URL` | Override the API base URL (default: `https://api.codesandbox.io`) |

# @together-sandbox/sdk

TypeScript SDK for the Together Sandbox API.

## Installation

### From GitHub Releases (Recommended)

Since the package is not published to npm, install it directly from GitHub Releases:

```bash
# Latest version
npm install https://github.com/togethercomputer/together-sandbox/releases/latest/download/together-sandbox-sdk.tgz

# Specific version
npm install https://github.com/togethercomputer/together-sandbox/releases/download/v1.0.0/together-sandbox-sdk.tgz
```

### With Authentication (Private Repositories)

For private repositories, authenticate using a Personal Access Token:

```bash
# Using a GitHub PAT
npm install https://YOUR_TOKEN@github.com/togethercomputer/together-sandbox/releases/download/v1.0.0/together-sandbox-sdk.tgz
```

### Using yarn or pnpm

```bash
# yarn
yarn add https://github.com/togethercomputer/together-sandbox/releases/download/v1.0.0/together-sandbox-sdk.tgz

# pnpm
pnpm add https://github.com/togethercomputer/together-sandbox/releases/download/v1.0.0/together-sandbox-sdk.tgz
```

### In package.json

Add to your `package.json` dependencies:

```json
{
  "dependencies": {
    "@together-sandbox/sdk": "https://github.com/togethercomputer/together-sandbox/releases/download/v1.0.0/together-sandbox-sdk.tgz"
  }
}
```

## Quick Start

```typescript
import { TogetherSandbox } from "@together-sandbox/sdk";

const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY });

// Start a sandbox — URL/token wiring is handled automatically
const sandbox = await sdk.sandboxes.start("your-sandbox-id");

// Read a file
const file = await sandbox.files.read({ path: { path: "/package.json" } });
console.log(file.data);

// Run a command
const exec = await sandbox.execs.create({
  body: { command: "node", args: ["-e", 'console.log("hello")'] },
});

// Shutdown when done
await sandbox.shutdown();
```

### Static factory

```typescript
import { Sandbox } from "@together-sandbox/sdk";

const sandbox = await Sandbox.start("your-sandbox-id", {
  apiKey: process.env.TOGETHER_API_KEY,
});
```

## Snapshots

Snapshots let you create pre-configured sandbox environments from a Dockerfile or public Docker image:

```typescript
// Build from a local Dockerfile
const result = await sdk.snapshots.create({
  context: "./my-app", // path to the Docker build context
  dockerfile: "./Dockerfile", // optional — defaults to Dockerfile in context
  alias: "my-app@latest", // optional
});

// Register a public Docker image
const result = await sdk.snapshots.create({
  image: "node:20-alpine",
  alias: "node@20", // optional
});

console.log(result.snapshotId); // pass to sdk.sandboxes.start()
console.log(result.alias); // "my-app@latest"
```

## Low-level Usage (Advanced)

The generated clients are still fully exported for direct use:

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

| Variable            | Description                                                       |
| ------------------- | ----------------------------------------------------------------- |
| `TOGETHER_API_KEY`  | Your Together / CodeSandbox API key                               |
| `TOGETHER_BASE_URL` | Override the API base URL (default: `https://api.codesandbox.io`) |

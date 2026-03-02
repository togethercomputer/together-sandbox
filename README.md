# Together Sandbox

Tools for working with Together AI sandboxes: a CLI, a TypeScript SDK, and a Python SDK.

## CLI

### Installation

```bash
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash
```

This installs `together-sandbox` to `/usr/local/bin`. To install a specific version or to a different directory:

```bash
VERSION=v1.2.3 bash <(curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh)
INSTALL_DIR=$HOME/.local/bin bash <(curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh)
```

### Authentication

Set your Together AI API key:

```bash
export TOGETHER_API_KEY=your_api_key
```

### Commands

#### `sandboxes`

```
together-sandbox sandboxes list [options]
  -o, --output     Comma-separated fields: id,title,privacy,tags,createdAt,updatedAt
  -t, --tags       Filter by tags (comma-separated)
  -s, --status     Filter by status (running)
  -p, --page       Page number
      --page-size  Items per page
      --since      Filter by creation date
      --order-by   Order by field (inserted_at, updated_at)
      --direction  Sort direction (asc, desc)
  -l, --limit      Maximum number of sandboxes to list (default: 100)

together-sandbox sandboxes fork <id>

together-sandbox sandboxes hibernate [id]    # reads from stdin if no ID given

together-sandbox sandboxes shutdown [id]     # reads from stdin if no ID given
```

#### `host-tokens`

```
together-sandbox host-tokens list <sandbox-id>

together-sandbox host-tokens create <sandbox-id> --expires-at <date>
  -e, --expires-at  Expiration date in ISO 8601 format (e.g. 2024-12-31T23:59:59Z)

together-sandbox host-tokens update <sandbox-id> <host-token-id> [--expires-at <date>]

together-sandbox host-tokens revoke <sandbox-id> [host-token-id]
  -a, --all  Revoke all tokens for the sandbox
```

#### `preview-hosts`

```
together-sandbox preview-hosts list

together-sandbox preview-hosts add <host>

together-sandbox preview-hosts remove <host>

together-sandbox preview-hosts clear
```

#### `build`

Builds and deploys a sandbox from the current directory.

```bash
together-sandbox build
```

---

## TypeScript SDK

> **Note:** The package is not yet published. The instructions below show how to install it once it is available on npm.

```bash
npm install @together-sandbox/sdk
```

### Usage

```typescript
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

// Create an exec and stream its status via SSE
const execResult = await sandbox.createExec({
  client: sandboxClient,
  body: { command: "bash", args: ["-c", "echo hello"] },
});

const { stream } = await sandbox.streamExecsList({ client: sandboxClient });
for await (const event of stream) {
  const exec = event.execs.find((e) => e.id === execResult.data.id);
  if (exec?.status === "finished" || exec?.status === "stopped") break;
}

// Shut down the sandbox when done
await api.vmShutdown({ client, path: { id: sandboxId } });
```

---

## Python SDK

> **Note:** The package is not yet published. The instructions below show how to install it once it is available on PyPI.

```bash
pip install together-sandbox
```

Requires Python 3.12+.

### Usage

```python
import asyncio, os
from together_sandbox.api import APIClient as ApiClient, ClientConfig, HttpxTransport
from together_sandbox.sandbox import APIClient as SandboxClient
from together_sandbox.sandbox import ClientConfig as SandboxConfig, HttpxTransport as SandboxTransport
from together_sandbox.sandbox.models.create_exec_request import CreateExecRequest

async def main():
    api_key = os.environ["TOGETHER_API_KEY"]
    base_url = os.environ.get("TOGETHER_BASE_URL", "https://api.codesandbox.io")

    async with ApiClient(ClientConfig(base_url=base_url),
                         transport=HttpxTransport(base_url, bearer_token=api_key)) as client:
        # Fork a sandbox from a template
        fork = await client.sandbox.sandbox_fork("your-template-id")
        sandbox_id = fork.data_.id_

        # Start the sandbox
        start = await client.vm.vm_start(sandbox_id)
        pint_url, pint_token = start.data_.pint_url, start.data_.pint_token

        # Connect to the running sandbox via Pint
        async with SandboxClient(SandboxConfig(base_url=pint_url),
                                  transport=SandboxTransport(pint_url, bearer_token=pint_token)) as sb:
            # Create an exec and stream its status via SSE
            exec_item = await sb.execs.create_exec(
                CreateExecRequest(command="bash", args=["-c", "echo hello"])
            )
            async for event in sb.execs.stream_execs_list():
                our = next((e for e in event.get("execs", []) if e.get("id") == exec_item.id_), None)
                if our and our["status"] in ("finished", "stopped"):
                    break

        # Shut down when done
        await client.vm.vm_shutdown(sandbox_id)

asyncio.run(main())
```

### Regenerating clients

If the OpenAPI specs change, regenerate all clients from the repo root:

```bash
bash generate.sh
```

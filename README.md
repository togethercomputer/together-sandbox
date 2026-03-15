# Together Sandbox

Tools for working with Together AI sandboxes: a CLI, a TypeScript SDK, and a Python SDK.

## Quick Start

All three components can be installed directly from GitHub without npm or PyPI publication:

```bash
# CLI (latest version)
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash

# TypeScript SDK (latest version)
npm install https://github.com/togethercomputer/together-sandbox/releases/latest/download/together-sandbox-sdk.tgz

# Python SDK (latest from main branch)
pip install "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"
```

For production use, we recommend pinning to a specific version. See the installation sections below for details.

---

## CLI

### Installation

Install via curl:

```bash
# Latest version
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash

# Specific version (recommended for production)
VERSION=v1.2.0 curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash
```

This installs `together-sandbox` to `/usr/local/bin`. To install to a different directory:

```bash
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

### Installation

Install from GitHub Releases:

```bash
# Latest version
npm install https://github.com/togethercomputer/together-sandbox/releases/latest/download/together-sandbox-sdk.tgz

# Specific version (recommended for production)
npm install https://github.com/togethercomputer/together-sandbox/releases/download/v1.2.0/together-sandbox-sdk.tgz
```

For private repositories, authenticate with a Personal Access Token:

```bash
npm install https://YOUR_TOKEN@github.com/togethercomputer/together-sandbox/releases/download/v1.2.0/together-sandbox-sdk.tgz
```

### In package.json

```json
{
  "dependencies": {
    "@together-sandbox/sdk": "https://github.com/togethercomputer/together-sandbox/releases/download/v1.0.0/together-sandbox-sdk.tgz"
  }
}
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

### Installation

Install from Git:

```bash
# Latest from main branch
pip install "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"

# Specific version (recommended for production)
pip install "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git@v1.2.0#subdirectory=together-sandbox-python"
```

For private repositories, use SSH:

```bash
pip install "git+ssh://git@github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"
```

### In requirements.txt

```text
together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python
```

**Requires Python 3.12+**

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

---

## Verifying Installation

After installing any component, verify it works correctly:

### CLI

```bash
# Check the version
together-sandbox --version

# Test with API (requires TOGETHER_API_KEY)
together-sandbox sandboxes list --limit 1
```

### TypeScript SDK

Create a test file `test-sdk.mjs`:

```javascript
import { createApiClient, createApiConfig } from "@together-sandbox/sdk";

const client = createApiClient(
  createApiConfig({
    baseUrl: "https://api.codesandbox.io",
    headers: { Authorization: `Bearer ${process.env.TOGETHER_API_KEY}` },
  }),
);

const result = await client.GET("/api/sandboxes");
console.log("Found", result.data.data.length, "sandboxes");
```

Run it:

```bash
node test-sdk.mjs
```

### Python SDK

Create a test file `test_sdk.py`:

```python
import asyncio
import os
from together_sandbox.api import APIClient, ClientConfig, HttpxTransport

async def main():
    async with APIClient(
        ClientConfig(base_url="https://api.codesandbox.io"),
        transport=HttpxTransport("https://api.codesandbox.io", bearer_token=os.environ["TOGETHER_API_KEY"]),
    ) as client:
        result = await client.sandbox.sandbox_list()
        print(f"Found {len(result.data_)} sandboxes")

asyncio.run(main())
```

Run it:

```bash
python test_sdk.py
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| **CLI not found** | Ensure `/usr/local/bin` is in your PATH, or use `INSTALL_DIR` |
| **TypeScript SDK 404** | Verify the release exists and you have repository access |
| **Python SDK install fails** | Ensure you have git installed and repository access |
| **Authentication errors** | Check your `TOGETHER_API_KEY` environment variable |

---

### Regenerating clients

If the OpenAPI specs change, regenerate all clients from the repo root:

```bash
bash generate.sh
```

---

## Development

### Testing the Release Workflow Locally

Before creating a tag, you can test the release workflow locally to ensure everything builds correctly:

```bash
# 1. Install dependencies
npm ci

# 2. Build the TypeScript SDK
cd together-sandbox-typescript && npm run build && cd ..

# 3. Pack the TypeScript SDK to verify tarball creation
npm pack --workspace=together-sandbox-typescript
# This creates together-sandbox-sdk-*.tgz

# 4. Verify the tarball contents
tar -tzf together-sandbox-sdk-*.tgz

# 5. Test installation in a clean directory
mkdir /tmp/test-sdk && cd /tmp/test-sdk
npm init -y
npm install /path/to/together-sandbox/together-sandbox-sdk-*.tgz

# 6. Build CLI binaries (requires Bun)
cd /path/to/together-sandbox/together-sandbox-cli
bun build --compile --minify src/main.tsx --target=bun-linux-x64 --outfile dist/test-binary

# 7. Test the CLI binary
./dist/test-binary --version
```

## Release Process

This project uses [Release Please](https://github.com/googleapis/release-please) for automated releases.

1. Use [conventional commits](https://www.conventionalcommits.org/) for all changes:
   - `feat:` for new features (minor version bump)
   - `fix:` for bug fixes (patch version bump)
   - `feat!:` for breaking changes (major version bump)
   - `docs:`, `chore:`, `refactor:` for non-release changes

2. When ready to release, merge the automatically-created Release PR

3. The workflow will automatically:
   - Create a new version tag
   - Generate/update the CHANGELOG.md
   - Build and upload SDK tarball and CLI binaries

### Manual Release Testing

Before merging a Release PR, you can test the build process locally:

```bash
# 1. Install dependencies
npm ci

# 2. Build the TypeScript SDK
cd together-sandbox-typescript && npm run build && cd ..

# 3. Pack the TypeScript SDK to verify tarball creation
npm pack --workspace=together-sandbox-typescript
# This creates together-sandbox-sdk-*.tgz

# 4. Verify the tarball contents
tar -tzf together-sandbox-sdk-*.tgz

# 5. Test installation in a clean directory
mkdir /tmp/test-sdk && cd /tmp/test-sdk
npm init -y
npm install /path/to/together-sandbox/together-sandbox-sdk-*.tgz

# 6. Build CLI binaries (requires Bun)
cd /path/to/together-sandbox/together-sandbox-cli
bun build --compile --minify src/main.tsx --target=bun-linux-x64 --outfile dist/test-binary

# 7. Test the CLI binary
./dist/test-binary --version
```

# Together Sandbox

Tools for working with Together AI sandboxes: a CLI, a TypeScript SDK, and a Python SDK.

## Quick Start

All three components require authentication with the [GitHub CLI](https://cli.github.com/) (`gh auth login`):

```bash
# CLI
GITHUB_TOKEN=$(gh auth token) curl -fsSL -H "Authorization: Bearer $(gh auth token)" \
  https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash

# TypeScript SDK
gh release download --repo togethercomputer/together-sandbox --pattern "together-sandbox-sdk.tgz" -D /tmp \
  && npm install /tmp/together-sandbox-sdk.tgz

# Python SDK
pip install "together-sandbox @ git+https://$(gh auth token)@github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"
```

---

## CLI

### Installation

Requires authentication with the [GitHub CLI](https://cli.github.com/) (`gh auth login`):

```bash
GITHUB_TOKEN=$(gh auth token) curl -fsSL -H "Authorization: Bearer $(gh auth token)" \
  https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash
```

This installs `together-sandbox` to `/usr/local/bin`. To install a specific version or to a different directory:

```bash
GITHUB_TOKEN=$(gh auth token) VERSION=v1.2.3 bash <(curl -fsSL -H "Authorization: Bearer $(gh auth token)" \
  https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh)

GITHUB_TOKEN=$(gh auth token) INSTALL_DIR=$HOME/.local/bin bash <(curl -fsSL -H "Authorization: Bearer $(gh auth token)" \
  https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh)
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

Install directly from GitHub Releases using the [GitHub CLI](https://cli.github.com/) (`gh auth login`):

```bash
# Latest version
gh release download --repo togethercomputer/together-sandbox --pattern "together-sandbox-sdk.tgz" -D /tmp \
  && npm install /tmp/together-sandbox-sdk.tgz

# Specific version
gh release download v1.0.0 --repo togethercomputer/together-sandbox --pattern "together-sandbox-sdk.tgz" -D /tmp \
  && npm install /tmp/together-sandbox-sdk.tgz
```

### Usage

```typescript
import { TogetherSandbox } from "@together-sandbox/sdk";

const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY });

// Start a sandbox — URL/token wiring is handled automatically
const sandbox = await sdk.sandboxes.start("your-sandbox-id");

// Read a file
const file = await sandbox.files.read({ path: { path: "/package.json" } });

// Run a command
const exec = await sandbox.execs.create({
  body: { command: "bash", args: ["-c", "echo hello"] },
});

// Shutdown when done
await sandbox.shutdown();
```

The low-level generated clients are also available for advanced use. See the [TypeScript SDK README](together-sandbox-typescript/README.md) for details.

---

## Python SDK

### Installation

Install directly from the GitHub repository using the [GitHub CLI](https://cli.github.com/) (`gh auth login`):

```bash
# Latest from main branch
pip install "together-sandbox @ git+https://$(gh auth token)@github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"

# Specific version (tag)
pip install "together-sandbox @ git+https://$(gh auth token)@github.com/togethercomputer/together-sandbox.git@v1.0.0#subdirectory=together-sandbox-python"
```

**Requires Python 3.12+**

### Usage

```python
import asyncio
from together_sandbox import TogetherSandbox

async def main():
    # api_key defaults to TOGETHER_API_KEY environment variable
    sdk = TogetherSandbox(api_key="your-api-key")

    # Start a sandbox — URL/token wiring is handled automatically
    async with await sdk.sandboxes.start("your-sandbox-id") as sb:
        content = await sb.files.read_file("/package.json")
        print(content)

asyncio.run(main())
```

The low-level generated clients are also available for advanced use. See the [Python SDK README](together-sandbox-python/README.md) for details.

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
| **TypeScript SDK 404** | Verify the release exists and run `gh auth login` |
| **Python SDK install fails** | Ensure you have git installed and run `gh auth login` |
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

### Creating a Release

1. Ensure all changes are committed and pushed
2. Create and push a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. The GitHub Actions workflow will automatically:
   - Build the TypeScript SDK
   - Pack it into `together-sandbox-sdk.tgz`
   - Build CLI binaries for all platforms
   - Create a GitHub Release with all artifacts

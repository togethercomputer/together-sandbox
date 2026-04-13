# Together Sandbox

Tools for working with Together AI sandboxes: a CLI, a TypeScript SDK, and a Python SDK.

## Quick Start

All three components can be installed directly from GitHub without npm or PyPI publication:

```bash
# CLI
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash

# TypeScript SDK
npm install https://github.com/togethercomputer/together-sandbox/releases/latest/download/together-sandbox-sdk.tgz

# Python SDK
pip install "together-sandbox @ git+https://github.com/togethercomputer/together-sandbox.git#subdirectory=together-sandbox-python"
```

Set your Together AI API key:

```bash
export TOGETHER_API_KEY=your_api_key
```

## CLI

### `sandboxes`

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

### `build`

Builds and deploys a sandbox from the current directory.

```bash
together-sandbox build
```

---

## TypeScript SDK

```typescript
import { TogetherSandbox } from "@together-sandbox/sdk";

const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY });

// Start a sandbox — URL/token wiring is handled automatically
const sandbox = await sdk.sandboxes.start("your-sandbox-id");

// Read a file — returns the file content as a string
const content = await sandbox.files.read("/package.json");
console.log(content);

// Run a command
const exec = await sandbox.execs.create({
  command: "bash",
  args: ["-c", "echo hello"],
});

// Shutdown when done
await sandbox.shutdown();
```

The low-level generated clients are also available for advanced use. See the [TypeScript SDK README](together-sandbox-typescript/README.md) for details.

---

## Python SDK

```python
import asyncio
from together_sandbox import TogetherSandbox

async def main():
    # api_key defaults to TOGETHER_API_KEY environment variable
    sdk = TogetherSandbox(api_key="your-api-key")

    # Start a sandbox — URL/token wiring is handled automatically
    async with await sdk.sandboxes.start("your-sandbox-id") as sb:
        content = await sb.files.read("/package.json")
        print(content)

asyncio.run(main())
```

The low-level generated clients are also available for advanced use. See the [Python SDK README](together-sandbox-python/README.md) for details.

---


### Troubleshooting

| Issue | Solution |
|-------|----------|
| **CLI not found** | Ensure `/usr/local/bin` is in your PATH, or use `INSTALL_DIR` |
| **TypeScript SDK 404** | Verify the release exists and you have repository access |
| **Python SDK install fails** | Ensure you have git installed and repository access |
| **Authentication errors** | Check your `TOGETHER_API_KEY` environment variable |

---

## Development

### Regenerating clients

If the OpenAPI specs change, regenerate all clients from the repo root:

```bash
bash generate.sh
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

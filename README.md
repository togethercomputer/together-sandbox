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

### `build`

Builds and deploys a sandbox from the current directory.

```bash
together-sandbox build <directory>
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

| Issue                        | Solution                                                      |
| ---------------------------- | ------------------------------------------------------------- |
| **CLI not found**            | Ensure `/usr/local/bin` is in your PATH, or use `INSTALL_DIR` |
| **TypeScript SDK 404**       | Verify the release exists and you have repository access      |
| **Python SDK install fails** | Ensure you have git installed and repository access           |
| **Authentication errors**    | Check your `TOGETHER_API_KEY` environment variable            |

---

## Development

### Regenerating clients

If the OpenAPI specs change, regenerate all clients from the repo root:

```bash
bash generate.sh
```

## Release Process

Releases are fully automated via **release-please** — no manual tagging or version bumping required.

### How it works

1. **Merge PRs to `main` using Conventional Commits** — the commit type determines what kind of release is created:
   - `feat:` → minor version bump
   - `fix:` → patch version bump
   - `feat!:` / `BREAKING CHANGE:` → major version bump
   - `chore:`, `docs:`, etc. → no release

2. **release-please opens a "Release PR"** automatically, accumulating changes and
   updating `CHANGELOG.md` plus all three version files in sync:
   - `together-sandbox-typescript/package.json`
   - `together-sandbox-cli/package.json`
   - `together-sandbox-python/pyproject.toml`

3. **Merge the Release PR** → release-please creates the GitHub Release and tag automatically.

4. **The `build-and-upload` job triggers** and:
   - Regenerates SDK clients (`bash generate.sh`)
   - Builds and packs the TypeScript SDK → `together-sandbox-sdk.tgz`
   - Compiles CLI binaries for all 5 platforms (darwin arm64/x64, linux x64/arm64, windows x64)
   - Uploads all artifacts to the GitHub Release

The only human action required is keeping commits conventional and merging the Release PR when ready to ship.

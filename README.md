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

## Docs

- [CLI](./docs/cli.md)
- [TypeScript SDK](./docs/typescript-sdk.md)
- [Python SDK](./docs/python-sdk.md)

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

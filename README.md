# Together Sandbox

Tools for working with Together AI sandboxes: a CLI, a TypeScript SDK, and a Python SDK.

## Quick Start

```bash
# CLI
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash

# TypeScript SDK
npm install together-sandbox

# Python SDK
pip install together-sandbox
```

## Get an API key

All three packages authenticate via the `TOGETHER_API_KEY` environment variable.

1. Sign in (or sign up) at [together.ai](https://together.ai).
2. Open your project's [API keys page](https://api.together.ai/settings/projects/~current/api-keys).
3. Click **Create key**, give it a name, and copy the value.
4. Export it in your shell (or add it to your `.env`):

   ```bash
   export TOGETHER_API_KEY="your-key-here"
   ```

## Documentation

The canonical docs live in [`docs/`](./docs/) and are the single source of truth:

- [Sandboxes and Snapshots](./docs/sandboxes.md)
- [Harbor Integration Guide](https://github.com/codesandbox/harbor/tree/integrate-with-together-sandbox-sdk#guide)
- [Tinker + Harbor recipe](https://github.com/togethercomputer/tinker-cookbook/tree/harbor-together/tinker_cookbook/recipes/harbor_rl)
- [CLI](./docs/cli.md)
- [TypeScript SDK](./docs/typescript-sdk.md)
- [Python SDK](./docs/python-sdk.md)

### Bundled per-SDK docs

Each published SDK ships a copy of the docs it needs (its own SDK reference,
the CLI reference, and the sandboxes/snapshots concepts) plus a top-level
`LLMS.md` guide. They land inside the npm tarball and the Python wheel so
agents and tools that introspect installed packages can discover them without
hitting the network:

| Package                  | After install, docs live at                      |
| ------------------------ | ------------------------------------------------ |
| `together-sandbox` (npm) | `node_modules/together-sandbox/{LLMS.md,docs/}`  |
| `together-sandbox` (pip) | `site-packages/together_sandbox/{LLMS.md,docs/}` |

[`generate.sh`](./generate.sh) copies the relevant subset of `docs/`
into each SDK package and renders `LLMS.md` from
[`LLMS-template.md`](./LLMS-template.md) with per-package substitutions.

Generated outputs (`together-sandbox-*/docs/` and `together-sandbox-*/LLMS.md`)
are git-ignored. Edit the source in [`docs/`](./docs/) and
[`LLMS-template.md`](./LLMS-template.md) — never the generated copies.

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

4. **Three publish jobs fan out in parallel**, all gated on the release-please tag:
   - **`build-and-upload`** — compiles CLI binaries for all 5 platforms (darwin arm64/x64, linux x64/arm64, windows x64) and attaches them to the GitHub Release.
   - **`publish-npm`** — regenerates SDK clients, builds the TypeScript SDK, and runs `npm publish` to publish [`together-sandbox`](https://www.npmjs.com/package/together-sandbox) to npm using OIDC trusted publishing (no token).
   - **`publish-pypi`** — regenerates SDK clients, runs `python -m build`, and publishes [`together-sandbox`](https://pypi.org/project/together-sandbox/) to PyPI using OIDC trusted publishing (no token).

   Both publish jobs run inside protected GitHub Environments (`npm` and `pypi`) so deploys are restricted to `main`.

The only human action required is keeping commits conventional and merging the Release PR when ready to ship.

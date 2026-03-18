# Development Guide

This guide helps contributors get up and running with the Together Sandbox
repository, which contains a TypeScript SDK, a Python SDK, and a CLI — all
backed by auto-generated API clients.

---

## Architecture Overview

The codebase follows a **two-layer architecture**:

1. **Generated code** — low-level API clients produced from two OpenAPI specs
   (`api-openapi.json` and `sandbox-openapi.json`). These files are overwritten
   every time the code generators run. **Do not edit them by hand.**

2. **Hand-written code** — higher-level facades, public exports, tests, and the
   entire CLI. This is where most development happens and where contributions
   should go.

### What is generated (DO NOT edit)

| Location | Generator |
|----------|-----------|
| `together-sandbox-typescript/src/api-clients/api/` | `@hey-api/openapi-ts` |
| `together-sandbox-typescript/src/api-clients/sandbox/` | `@hey-api/openapi-ts` |
| `together-sandbox-python/together_sandbox/api/` | `pyopenapi-gen` |
| `together-sandbox-python/together_sandbox/sandbox/` | `pyopenapi-gen` |
| `together-sandbox-python/together_sandbox/core/` | `pyopenapi-gen` |

### What is hand-written (safe to edit)

| File(s) | Purpose |
|---------|---------|
| `together-sandbox-typescript/src/TogetherSandbox.ts` | TypeScript SDK facade |
| `together-sandbox-typescript/src/index.ts` | TypeScript public exports |
| `together-sandbox-typescript/src/TogetherSandbox.test.ts` | TypeScript unit tests (vitest) |
| `together-sandbox-python/together_sandbox/facade.py` | Python SDK facade |
| `together-sandbox-python/together_sandbox/__init__.py` | Python public exports |
| `together-sandbox-python/tests/test_facade.py` | Python unit tests (pytest) |
| `together-sandbox-cli/src/**` | Entire CLI (no generated code) |

The facade layer wraps the two generated clients (management API + in-sandbox
API) to handle connection routing, token management, and higher-level
ergonomics. This is where most SDK improvements belong.

---

## Prerequisites

| Tool | Purpose | Minimum Version |
|------|---------|----------------|
| Node.js | TypeScript SDK + CLI | 22 |
| npm | Workspace & dependency management | bundled with Node 22 |
| Bun | CLI binary compilation | latest |
| Python | Python SDK + code-generation scripts | 3.12 |
| pip | Python package management | bundled with Python |
| git | VCS, also needed by pip for VCS installs | any |

---

## Setting Up the TypeScript SDK & CLI

From the repo root, install all workspace dependencies in one step:

```bash
npm ci
```

This pulls in everything for both `together-sandbox-typescript` and
`together-sandbox-cli`.

**Build the TypeScript SDK:**

```bash
cd together-sandbox-typescript
npm run build          # tsc → dist/
```

**Build the CLI (development bundle):**

```bash
cd together-sandbox-cli
npm run build          # esbuild → dist/together-sandbox.mjs
```

**Build standalone CLI binaries (requires Bun):**

```bash
cd together-sandbox-cli
npm run build:binary           # native binary for your current platform
npm run build:binary:all       # all platforms (darwin-arm64, darwin-x64, linux-x64, linux-arm64, windows-x64)
```

---

## Setting Up the Python SDK

```bash
cd together-sandbox-python

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
# The [dev] extra includes pyopenapi-gen (the code generator)
pip install -e ".[dev]"
```

---

## Running the Test Suites

### TypeScript (vitest)

Tests live in `together-sandbox-typescript/src/TogetherSandbox.test.ts`.

```bash
# From the repo root
npx vitest run --project together-sandbox-typescript

# Or from the package directory
cd together-sandbox-typescript
npx vitest run        # single pass (no watch)
npx vitest            # watch mode
```

### Python (pytest)

Tests live in `together-sandbox-python/tests/`.

```bash
cd together-sandbox-python
source .venv/bin/activate

pytest                # run all tests
pytest -v             # verbose output
pytest tests/test_facade.py   # specific file
```

All Python tests use `unittest.mock` / `monkeypatch` — no network calls are
made, so tests run fully offline.

---

## Regenerating the Auto-Generated API Clients

### When to regenerate

Regenerate whenever either OpenAPI spec changes:

| Spec file | Describes |
|-----------|-----------|
| `api-openapi.json` | Management API (sandbox lifecycle, templates, preview hosts) |
| `sandbox-openapi.json` | In-VM Sandbox API (files, execs, tasks, ports, streams) |

### How to regenerate — all clients at once

```bash
# From the repo root
bash generate.sh
```

This script:

1. **Patches `api-openapi.json`** — promotes anonymous inline `data` objects to
   named `$ref` schemas (needed because the Python generator collapses them
   into a single `Data_` class otherwise).
2. **Regenerates the TypeScript SDK** — runs `npm run generate` inside
   `together-sandbox-typescript/`, which calls `@hey-api/openapi-ts` against
   both specs.
3. **Regenerates the Python SDK** — runs `bash generate.sh` inside
   `together-sandbox-python/`, which calls `pyopenapi-gen` against both specs
   with pre- and post-processing steps.

### How to regenerate — individual SDKs

**TypeScript only:**

```bash
cd together-sandbox-typescript
npm run generate
```

**Python only:**

```bash
cd together-sandbox-python
bash generate.sh
```

### Prerequisites for regeneration

- **TypeScript:** `@hey-api/openapi-ts` is already a devDependency — `npm ci`
  at the root is sufficient.
- **Python:** `pyopenapi-gen` is listed under the `[dev]` optional dependency
  group — install it with `pip install -e ".[dev]"`.

### Known quirks (already handled by generate.sh)

| Quirk | Root cause | Workaround |
|-------|-----------|------------|
| Python generates `Data_` for all response data | Anonymous inline objects in `api-openapi.json` | Root `generate.sh` promotes them to named schemas |
| `pyopenapi-gen` can't handle top-level `$ref` aliases | Generator limitation | Python `generate.sh` wraps aliases in `allOf` |
| Generated `__init__.py` contains literal `\n` | `pyopenapi-gen` bug | Python `generate.sh` post-processes the file |

---

## Environment Variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `TOGETHER_API_KEY` | SDK + CLI | Together AI / CodeSandbox API key |
| `TOGETHER_BASE_URL` | SDK | Override API base URL (default: `https://api.codesandbox.io`) |
| `VERSION` | `install.sh` | Override CLI release version to install |
| `INSTALL_DIR` | `install.sh` | Override CLI install directory (default: `/usr/local/bin`) |

---

## CI Workflows

| Workflow | Trigger | What it does |
|----------|---------|-------------|
| `pr-checks.yml` | Pull request to `main` | Validates release-please config; builds TypeScript SDK + CLI binaries |
| `release.yml` | Push to `main` | Runs release-please; builds, packs, and uploads artifacts to GitHub Release |

> **Note:** The PR workflow does **not** run the test suites automatically.
> Run tests locally before opening a PR.

---

## Tips

- **Commit before regenerating.** The generate script rewrites files in place.
- **Always activate the Python venv** before running Python commands.
- **Run tests before pushing:** `npx vitest run` (TypeScript) and `pytest` (Python).
- **Use `npm run build:binary`** locally for fast CLI iteration; reserve
  `build:binary:all` for CI and releases.

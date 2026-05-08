# Together Sandbox — Developer Guide

## Repo structure

```
together-sandbox/
├── together-sandbox-typescript/   # @together-sandbox/sdk (npm)
├── together-sandbox-python/       # together-sandbox (PyPI)
├── together-sandbox-cli/          # @together-sandbox/cli (npm, binary)
├── generate.sh                    # Re-generate all SDK clients from specs
├── api-openapi.json               # Management API OpenAPI spec
└── sandbox-openapi.json           # In-VM Sandbox API OpenAPI spec
```

All three packages share the same version number, bumped together by
**release-please** (see `release-please-config.json`).

## Code generation

Both SDKs are thin hand-written **facades** over auto-generated OpenAPI clients.
The generated code lives in:

- TypeScript: `together-sandbox-typescript/src/api-clients/`
- Python: `together-sandbox-python/together_sandbox/api/` and `.../sandbox/`

**Never edit generated files by hand.** All files ending in `.gen.ts` and every
file inside the `api/` or `sandbox/` sub-directories are overwritten on every
regeneration.

To regenerate after changing an OpenAPI spec:

```bash
bash generate.sh
```

This patches `api-openapi.json` (promotes inline schemas to named refs for the
Python generator), then runs `npm run generate` in the TypeScript package and
`bash generate.sh` in the Python package.

## Environment variables

| Variable                     | Purpose                                                |
| ---------------------------- | ------------------------------------------------------ |
| `CSB_API_KEY`                | Required. CSB AI API key.                              |
| `CSB_BASE_URL`               | Optional. Override management API base URL (CLI only). |
| `CODESANDBOX_SENTRY_ENABLED` | Optional. Set to `"true"` to enable Sentry in the CLI. |

## Commit conventions

Follow Conventional Commits. Prefix with the Jira ticket where applicable:

```
feat: add sandbox.files.stat() method
fix(CSB-1289): use binary-only upload for create file
chore: clean up readme and prep cli
```

Types: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`, `ci`.

## Release

Versions are managed by **release-please**. Do not bump versions manually.
All three package files (`package.json` ×2, `pyproject.toml`) must stay in
sync — release-please handles this via `extra-files` in `release-please-config.json`.

## Running tests

```bash
# TypeScript SDK unit tests
cd together-sandbox-typescript
npm test

# Python SDK tests (requires generated clients)
bash generate.sh          # from repo root first
cd together-sandbox-python
pip install ".[dev]"
pytest tests/ -v

# CLI typecheck (esbuild skips type checking at build time)
cd together-sandbox-cli
npm run typecheck
```

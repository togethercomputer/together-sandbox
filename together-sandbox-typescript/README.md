# @together-sandbox/sdk

TypeScript SDK for the Together Sandbox API.

[SDK Docs](../docs/typescript-sdk.md)

## Generating the API clients

The SDK wraps two auto-generated OpenAPI clients. Regenerate them whenever an
OpenAPI spec changes (both specs live in the repo root):

```bash
# From the repo root
bash generate.sh
```

This runs `npm run generate` inside `together-sandbox-typescript/`, which writes
the output to:

- `src/api-clients/api/` — management API client
- `src/api-clients/sandbox/` — in-VM sandbox API client

**Never edit those directories by hand** — they are overwritten on every run.

## Running tests

### Unit tests

```bash
cd together-sandbox-typescript
npm test
```

### Type checking

esbuild (used for the production build) skips TypeScript type checking at build
time. Run the type checker separately to catch type errors:

```bash
cd together-sandbox-typescript
npm run typecheck
```

### End-to-end tests

E2E tests hit the real API and require `TOGETHER_API_KEY` to be set and Docker
to be running locally (snapshot builds use a Docker build context under the
hood).

```bash
cd together-sandbox-typescript
TOGETHER_API_KEY=your-api-key npm run test:e2e
```

## Environment variables

| Variable            | Description                                                                             |
| ------------------- | --------------------------------------------------------------------------------------- |
| `TOGETHER_API_KEY`  | Required. Your Together AI API key.                                                     |
| `TOGETHER_BASE_URL` | Optional. Override the management API base URL (default: `https://api.codesandbox.io`). |

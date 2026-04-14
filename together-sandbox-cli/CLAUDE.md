# CLI — Developer Guide

Package: `@together-sandbox/cli` · binary: `together-sandbox`

## File layout

```
src/
├── main.ts                  # CLI entry point (yargs wiring)
├── commands/
│   └── build.ts             # `together-sandbox build` command
└── utils/
    ├── api.ts               # API client factory + retryWithDelay
    ├── constants.ts         # Env var resolution helpers
    ├── docker.ts            # Docker build/push helpers
    ├── files.ts             # Directory hashing for upload
    ├── misc.ts              # sleep(), base32Encode()
    └── sentry.ts            # Optional Sentry instrumentation
```

## Important: esbuild skips TypeScript type-checking

The CLI is bundled with **esbuild** which transpiles but does not type-check.
Always run the explicit typecheck step before merging:

```bash
npm run typecheck   # runs tsc --noEmit
```

Missing imports and type errors will not surface at build time — they will
only be caught by `typecheck` or at runtime.

## API client conventions

### Always use `createClient` from `utils/api.ts`

Never call `createApiClient` / `createConfig` directly in commands. Use the
`createClient(apiKey, instrumentation?)` factory which automatically:

- Injects the `Authorization: Bearer` header
- Adds the `traceparent` tracing header to every request
- Optionally routes through Sentry via `instrumentedFetch`

```typescript
// ✅ correct
const apiClient = createClient(apiKey, instrumentedFetch);

// ❌ wrong — bypasses tracing and Sentry
const apiClient = createApiClient(
  createConfig({ headers: { Authorization: `Bearer ${apiKey}` } }),
);
```

### Use `getInferredApiKey()` for key resolution

Always call `getInferredApiKey()` from `utils/constants.ts` rather than
reading `process.env.TOGETHER_API_KEY` directly. Do not introduce new
`CSB_API_KEY` fallbacks — that is a legacy alias.

## TypeScript conventions

- **No `@ts-ignore`.** Use `// @ts-expect-error` with a comment explaining
  the suppression. Prefer fixing the type over suppressing it.
- **All functions must have explicit return-type annotations** on exported
  functions.

## Spinner conventions

Use `ora` for all user-facing progress feedback. Stream to `process.stdout`:

```typescript
const spinner = ora({ stream: process.stdout });
spinner.start("Doing something...");
try {
  // ...
  spinner.succeed("Done.");
} catch (error) {
  spinner.fail(`Failed: ${(error as Error).message}`);
  throw error;
}
```

Strip ANSI codes with `stripAnsiCodes()` before passing subprocess output to
`spinner.text` — terminal control sequences corrupt spinner rendering.

## Docker helpers

All Docker interactions go through `utils/docker.ts`:

- `isDockerAvailable()` — check before any Docker operation
- `prepareDockerBuild(dir, onOutput?)` — locate or create a Dockerfile, returns a `cleanupFn`
- `buildDockerImage(options)` — build with `--platform linux/<arch>`
- `dockerLogin(options)` — uses `--password-stdin` (never pass password as a CLI arg)
- `pushDockerImage(name, onOutput?)` — push to registry

Always call the returned `cleanupFn` in a `finally` block to remove temporary
Dockerfiles even if the build fails.

## Build

```bash
npm run build          # esbuild bundle → dist/together-sandbox.mjs
npm run typecheck      # tsc --noEmit (always run before merging)
```

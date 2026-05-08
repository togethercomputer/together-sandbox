# CLI — Developer Guide

Package: `@together-sandbox/cli` · binary: `together-sandbox`

## Important: esbuild skips TypeScript type-checking

The CLI is bundled with **esbuild** which transpiles but does not type-check.
Always run the explicit typecheck step before merging:

```bash
npm run typecheck   # runs tsc --noEmit
```

Missing imports and type errors will not surface at build time — they will
only be caught by `typecheck` or at runtime.

## Build

```bash
npm run build          # esbuild bundle → dist/together-sandbox.mjs
npm run typecheck      # tsc --noEmit (always run before merging)
```

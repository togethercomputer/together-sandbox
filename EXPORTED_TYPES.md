# Exported types — how we think about the public surface

Both SDKs (`together-sandbox` for npm, `together-sandbox` for PyPI) are thin
hand-written facades over **auto-generated** OpenAPI clients. This document is
the policy for what types we expose to consumers and why.

## The rule

> **The public API surface consists only of hand-written facade types. A
> generated type must never be exported, re-exported, or appear in a public
> method signature.**

"Generated" means anything produced by a code generator:

- **TypeScript**: everything under `together-sandbox-typescript/src/api-clients/`
  (`@hey-api/openapi-ts` output) and the `@hey-api/client-fetch` runtime types
  (`Client`, `Config`, `RequestOptions`, `Middleware`, …).
- **Python**: everything under `together-sandbox-python/together_sandbox/_api/`
  and `together-sandbox-python/together_sandbox/_sandbox_client/`
  (`openapi-python-client` output), including the attrs models, their `UNSET`
  sentinels, `to_dict`/`from_dict`, `additional_properties`, and the generated
  enums.

The underscore prefix on the Python packages (`_api`, `_sandbox_client`) is the
signal that they are private. The TypeScript clients live under `api-clients/`
and are simply never re-exported from `index.ts`.

## Why

Generated symbols are a bad public contract:

- They are **overwritten on every `bash generate.sh`** — we don't own them.
- They **shift when a spec changes**: a renamed field, a widened enum, or a
  generator upgrade silently changes a type consumers depend on.
- They **carry generator machinery** that isn't part of the data contract:
  attrs `UNSET`/`to_dict`/`additional_properties` in Python, and ~250 lines of
  `Client`/`Config`/`Interceptors`/`RequestResult` plumbing per client in
  TypeScript's `.d.ts`.

Hand-written facade types are small, stable, documented, and ours to evolve
deliberately.

## How conversion happens (at the facade boundary)

**TypeScript.** The in-VM sandbox API is already camelCase on the wire, so most
facade types are structurally identical to the generated ones — we just
annotate the method's return type with the hand-written type and the generated
value flows through. Management-API responses are snake_case and are converted
to camelCase at the boundary with `camelCaseKeys` (`src/utils.ts`), e.g.
`SandboxInfo` (in `Sandboxes.ts`) and `Snapshot` (in `Snapshots.ts`).

Internal-only constructors that take generated clients (`Sandbox`,
`SandboxesNamespace`, `SnapshotsNamespace`) are marked `/** @internal */` and
stripped from the published declarations via `"stripInternal": true` in
`tsconfig.json`. This is what keeps the `@hey-api` plumbing out of
`dist/index.d.ts`.

**Python.** Generated models are attrs classes, so we convert at runtime.
`together_sandbox/types.py` holds the hand-written `@dataclass` facade types and
the boundary adapters (`_<thing>_from_model` for generated models,
`_<thing>_from_dict` for raw SSE payloads). Every facade method that would
otherwise return a generated model/dict calls an adapter first.

## Casing

- **TypeScript** public types are **camelCase** (`byteSize`, `createdAt`,
  `isDir`).
- **Python** public types are **snake_case** (`byte_size`, `created_at`,
  `is_dir`) per PEP 8.

Timestamps are `string` (ISO 8601) in TS and `datetime` in Python; enum-like
fields are string-literal unions in both (`Literal[...]` in Python).

## Canonical export sets

These are the source of truth. Keep `index.ts` / `__init__.py` in sync.

### TypeScript (`src/index.ts`)

Values: `TogetherSandbox`, `Sandbox`, `HttpError`.

Types: `TogetherSandboxConfig`, `RetryConfig`, `RetryContext`, `SandboxInfo`,
`SandboxStatus`, `StopReason`, `StartType`, `RecoveryStatus`,
`CreateSandboxParams`, `StartOptions`, `WatchOptions`, `FileInfo`,
`WatcherEvent`, `WatcherEventType`, `ExecInfo`, `ExecStatus`, `ExecStreamKind`,
`CreateExecParams`, `ExecOutputEvent`, `ExecStdinInput`, `ExecResult`,
`PortInfo`, `Snapshot`, `SnapshotArchitecture`, `CreateSnapshotParams`,
`CreateContextSnapshotParams`, `CreateImageSnapshotParams`,
`CreateSnapshotResult`, `SnapshotProgress`.

### Python (`together_sandbox/__init__.py` `__all__`)

Classes: `TogetherSandbox`, `Sandbox`, `HttpError`.

Types: `RetryConfig`, `RetryContext`, `SandboxInfo`, `SandboxStatus`,
`StartType`, `StopReason`, `RecoveryStatus`, `FileInfo`, `WatcherEvent`,
`WatcherEventType`, `ExecInfo`, `ExecStatus`, `ExecStreamKind`,
`ExecOutputEvent`, `ExecResult`, `PortInfo`, `Snapshot`, `CreateSnapshotParams`,
`CreateContextSnapshotParams`, `CreateImageSnapshotParams`,
`CreateSnapshotResult`, `SnapshotProgress`.

The two SDKs differ where a language idiom differs: TS exposes parameter objects
(`CreateSandboxParams`, `CreateExecParams`, `StartOptions`, `WatchOptions`,
`ExecStdinInput`) that Python expresses as keyword arguments, so those names are
TS-only. The `SnapshotArchitecture` selection is internal in the Python SDK and
is not exported.

## Checklist — adding or changing a facade method

1. Does the return value or a parameter reference a generated type? If yes,
   add/extend a hand-written facade type (TS: `types.ts`/`Snapshots.ts`;
   Python: `types.py`) and an adapter, and convert at the boundary.
2. Add the new type to the canonical export set in `index.ts` / `__init__.py`
   **and** to the list in this file.
3. TypeScript: run `npm run build` and confirm `dist/index.d.ts` contains no
   `@hey-api`, `Client`/`Config`, or `api-clients` references and no generated
   model names (`ExecItem`, `ExecStdout`, `CreateExecRequest`, …). The
   `src/index.test.ts` surface test guards the runtime exports.
4. Python: confirm nothing under `_api`/`_sandbox_client` appears in a public
   signature, and that `from together_sandbox import <NewType>` works.

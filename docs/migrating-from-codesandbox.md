# Migrating from CodeSandbox SDK to Together Sandbox

This guide is for teams that integrated with the CodeSandbox SDK
(`@codesandbox/sdk`, docs at <https://codesandbox.io/docs/sdk>) and are moving
to Together Sandbox (`together-sandbox` on npm and PyPI, plus the
`together-sandbox` CLI).

- **[Part 1](#part-1--overview-for-humans)** is a human-readable overview: what
  changed, a feature map, and what is no longer supported.
- **[Part 2](#part-2--migration-reference-for-ai-agents)** is a precise,
  mechanical reference meant for AI coding agents (and humans) performing the
  migration: detection patterns, an ordered procedure, and before/after rewrite
  rules for every API.

---

# Part 1 — Overview (for humans)

## TL;DR

1. **New packages, new key.** `@codesandbox/sdk` → `together-sandbox`.
   `CSB_API_KEY` → `TOGETHER_API_KEY`. The `csb` CLI → `together-sandbox`.
2. **Templates are now snapshots.** Build them from a Dockerfile or an existing
   Docker image with `sdk.snapshots.create()` (or
   `together-sandbox snapshots create`). Existing CodeSandbox templates and
   sandboxes cannot be imported — rebuild them. There is no default template;
   every sandbox must be created from a snapshot you specify.
3. **No hibernate / resume.** The lifecycle is now
   `create → running → terminate`. A terminated sandbox is gone for good.
   "Hibernate" and "shutdown" both become *terminate with a snapshot*; "resume"
   becomes *create a new sandbox from that snapshot*.
4. **Sandbox IDs change on every "resume".** The new sandbox has a new ID.
   Store the latest ID (or, better, a snapshot alias) instead of a fixed ID.
5. **Ephemeral by default.** A sandbox created without a `terminationPolicy`
   takes no snapshot and is deleted on termination. Add `terminationPolicy` if
   you want its filesystem to survive.
6. **Disk only (for now).** Snapshots capture the filesystem, not memory.
   Running processes do not survive a terminate → create cycle; restart them
   with execs. Memory snapshots (true hibernate) are **coming soon**.
7. **No `connect()`.** `sdk.sandboxes.create()` returns an already-connected
   `Sandbox` with `files`, `directories`, `execs` and `ports`. Commands,
   terminals and interpreters are all unified into **execs**.
8. **Specs are explicit.** `vmTier` → `cpu` + `memoryBytes`, fixed at creation.

## Mental model: old vs new lifecycle

```
CodeSandbox SDK (old)                          Together Sandbox (new)
─────────────────────                          ──────────────────────
  create/fork ──► RUNNING ◄──┐                   create() ──► starting ──► running
                    │        │ resume()                                      │
       hibernate()  │        │ (same ID,                      terminate()    │
       (auto after  ▼        │  memory restored)                             ▼
       idle timeout) HIBERNATED ──(snapshot expires)─► disk-only      terminating
                    │                                  (CLEAN boot)          │
       shutdown()   ▼                                                        ▼
                  SHUT DOWN ──resume()──► RUNNING (CLEAN boot)          terminated  (final)
                    │                                                        │
       delete()     ▼                                           snapshot aliased
                  DELETED                                       `sandbox:<id>`
                                                                             │
                                                  create({ snapshotAlias: "sandbox:<id>" })
                                                                             ▼
                                                              NEW sandbox (new ID), running
```

New statuses: `starting`, `running`, `terminating`, `terminated`,
`failed_to_start`, `recovering`, `unrecovered`. Why a sandbox is in its status
is always in `statusReason` (see [Sandboxes & Snapshots](./sandboxes.md)).

## Feature map

### Client, auth and packages

| CodeSandbox SDK | Together Sandbox | Notes |
| --- | --- | --- |
| `npm i @codesandbox/sdk` | `npm i together-sandbox` / `pip install together-sandbox` | Python SDK is new (async only). |
| `new CodeSandbox(apiKey?, opts)` | `new TogetherSandbox({ apiKey?, baseUrl?, retry? })` | |
| `CSB_API_KEY` | `TOGETHER_API_KEY` | CodeSandbox keys do not work. |
| `CSB_BASE_URL` / `opts.baseUrl` | `TOGETHER_BASE_URL` / `baseUrl` | |
| `opts.tracer` (OpenTelemetry) | — | Not supported. Wrap calls yourself. |
| `opts.fetch`, `opts.headers` | — | Not supported. |
| Ad-hoc retries, `RateLimitError` | Built-in retry (`RetryConfig`), `HttpError` | |
| `@codesandbox/sdk/browser`, `@codesandbox/sdk/node` (`connectToSandbox`) | — | Not supported. Call the SDK from your backend. |

### Lifecycle

| CodeSandbox SDK | Together Sandbox | Notes |
| --- | --- | --- |
| `sdk.sandboxes.create({ id: templateId })` | `sdk.sandboxes.create({ snapshotAlias \| snapshotId })` | Snapshot is required. Returns a connected `Sandbox`. |
| `sdk.sandboxes.hibernate(id)` (memory + disk) | `sdk.sandboxes.terminate(id, { snapshot: { aliases } })` | **Disk only today.** Memory snapshots coming soon. |
| `sdk.sandboxes.shutdown(id)` (disk only) | `sdk.sandboxes.terminate(id, { snapshot: { aliases } })` | Same call as hibernate until memory snapshots ship. |
| `sdk.sandboxes.resume(id)` | `sdk.sandboxes.create({ snapshotAlias: "sandbox:<id>" })` | Returns a **new** sandbox ID. |
| `sdk.sandboxes.restart(id)` | terminate with snapshot → create from `sandbox:<id>` | New ID. No agent-update step needed. |
| `sdk.sandboxes.delete(id)` | `sdk.sandboxes.terminate(id, { snapshot: null })` | Plus `sdk.snapshots.retire(id)` for snapshots you no longer need. |
| `sdk.sandboxes.fork(id)` / `create({ id: sandboxId })` | terminate parent with snapshot → create N from `sandbox:<parentId>` | No live fork: the parent stops. |
| Fork of a hibernated sandbox | create from its snapshot (`sandbox:<id>` or your alias) | Any number of sandboxes can start from one snapshot. |
| Auto-hibernate after `hibernationTimeoutSeconds` idle | `create({ ttl, terminationPolicy })` | `ttl` counts from **creation**, not idle time. No idle detection. |
| `automaticWakeupConfig` (wake on HTTP/WS) | — | Not supported. A terminated sandbox never wakes. |
| `sandbox.bootupType` (`RUNNING`/`CLEAN`/`RESUME`/`FORK`) | `sandbox.vmInfo.statusReason` | Every boot is effectively a clean boot today. |
| `sandbox.isUpToDate`, restart to update agent | — | Not needed. |
| Memory-snapshot retention (≈7 days), archive | Snapshot `ttl` you set; kept indefinitely by default | `terminationPolicy.snapshot.ttl`, `snapshots.retire()`. |
| — | Automatic crash recovery (`recovering`, `recoveryAt`) | New. |
| Reattach to a running sandbox by ID (`resume` + `connect`) | Keep the `Sandbox` object; a `connect(id)`-style method is **coming soon** | See [Reattaching](#reattaching-to-a-running-sandbox). |

### Sandbox options and management

| CodeSandbox SDK | Together Sandbox | Notes |
| --- | --- | --- |
| `vmTier: VMTier.Nano` / `VMTier.fromSpecs()` | `cpu`, `memoryBytes` | See [tier table](#vm-tiers--cpu--memorybytes). Max 16 vCPU / 32 GB. |
| `sandbox.updateTier()` (live resize) | — | Not supported. Terminate with snapshot, create with new specs. |
| `sandbox.updateHibernationTimeout()` | — | Not supported. `ttl` is fixed at creation. |
| `tags: string[]` | `tags: Record<string, string>` | |
| `title`, `description`, `path` | `tags` | Store them as tags if you need them. |
| `privacy` (`public` / `private` / `public-hosts` / `unlisted`) | — | Not supported. All ports are public. |
| `ipcountry` | — | Not supported. |
| `sdk.sandboxes.get(id)` | `sdk.sandboxes.get(id)` | Returns status, resources, tags, agent info — not title/privacy. |
| `sdk.sandboxes.list({ tags, status, orderBy, direction, pagination })` | `sdk.sandboxes.list({ tags, statuses, snapshotId, limit, cursor })` | Cursor-paginated `Page`. No ordering options. |
| `sdk.sandboxes.listRunning()` | `sdk.sandboxes.list({ statuses: ["running"] })` | Concurrency count/limit not exposed. |
| Custom sandbox IDs | — | IDs are platform-generated UUIDs; use tags. |

### Templates → snapshots

| CodeSandbox SDK | Together Sandbox | Notes |
| --- | --- | --- |
| `csb build <dir>` | `together-sandbox snapshots create --context <dir>` / `sdk.snapshots.create({ context })` | Remote build, no local Docker needed. |
| Template from a Docker image (beta) | `snapshots create --image <ref>` / `sdk.snapshots.create({ image })` | |
| `.codesandbox/Dockerfile`, `.devcontainer/devcontainer.json` | A plain `Dockerfile` | Dev Container spec and Docker Compose are not interpreted. |
| `--alias namespace@alias` | `--alias` / `alias` / `sdk.snapshots.alias(id, alias)` | Aliases are mutable pointers. |
| Template tag ID / template ID | Snapshot UUID or alias | |
| `--ports`, `--vm-tier`, `--vm-build-tier`, `--from-sandbox` | — | Not applicable. Specs are chosen per sandbox. |
| `--ci` | `--ci` | Prints only the snapshot ID on success. |
| — | `cacheKey` / `--cache-key` | New: reuse layer cache across builds. |
| Default "Universal" template | — | No default. Build or pick your own image. |
| `setupTasks` in `.codesandbox/tasks.json` | Dockerfile `RUN` steps, or execs after create | Not supported as a concept. |
| `tasks` in `.codesandbox/tasks.json` | `execs.create()` after create | Not supported as a concept. |
| Git-backed persistence of `/project/workspace` | Whole filesystem snapshot on terminate | `.gitignore` is not honoured; everything is captured. |

### Inside the sandbox

| CodeSandbox SDK | Together Sandbox | Notes |
| --- | --- | --- |
| `await sandbox.connect()` → `client` | the `Sandbox` returned by `create()` | |
| `client.fs.readTextFile` / `readFile` | `sandbox.files.read` | Returns a string (base64 for binary content). |
| `client.fs.writeTextFile` / `writeFile` | `sandbox.files.create` | Creates or overwrites. |
| `client.fs.batchWrite` | loop `files.create`, or upload a tarball and extract via exec | |
| `client.fs.readdir` | `sandbox.directories.list` | |
| `client.fs.mkdir` | `sandbox.directories.create` | Creates parents. |
| `client.fs.remove` | `sandbox.files.delete` / `sandbox.directories.delete` | |
| `client.fs.rename` | `sandbox.files.move` | |
| `client.fs.copy` | `sandbox.files.copy` | |
| `client.fs.stat` | `sandbox.files.stat` | Fields: `name, path, isDir, size, modTime`. |
| `client.fs.watch` | `sandbox.files.watch` | SSE stream. `excludes` → `ignorePatterns`. |
| `client.fs.download` (zip URL) | — | Not supported. Archive via exec, then read. |
| `client.commands.run` | `sandbox.execs.exec` | Returns `{ exitCode, output }`; does not throw on non-zero exit. |
| `client.commands.runBackground` | `sandbox.execs.create` | Then `streamOutput` / `getOutput`. |
| `command.kill()` | `sandbox.execs.delete(id)` | |
| `client.commands.getAll` | `sandbox.execs.list` | |
| `client.terminals.*` | `execs.create({ pty: true })` + `sendStdin` + `streamOutput` | |
| `client.interpreters.javascript/python` | `execs.exec("node", ["-e", code])` / `execs.exec("python3", ["-c", code])` | |
| `client.setup.*` | — | Not supported. |
| `client.tasks.*` | — | Not supported. Use execs. |
| `client.ports.getAll` / `get` | `sandbox.ports.list` | `{ port, address }`. |
| `client.ports.onDidPortOpen/Close` | `sandbox.ports.streamList` | SSE stream. |
| `client.ports.waitForPort` | poll `ports.list` | See [helper](#ports-and-preview-urls). |
| `createSession({ id, permission })` (per-user) | `execs.create({ user })` | Create the Linux user in the Dockerfile or with a root exec. No read/write permission model. |
| `createSession({ env })` / `connect({ env })` | `execs.create({ env })` / `execs.exec(cmd, args, { env })` | Per exec. |
| `createSession({ git })` | pass tokens via exec `env`, configure git via exec | |
| `client.disconnect/reconnect/keepActiveWhileConnected` | — | Not needed; the in-VM API is plain HTTP/SSE. |

### Previews and networking

| CodeSandbox SDK | Together Sandbox | Notes |
| --- | --- | --- |
| `https://<id>-<port>.csb.app` | `urlFormat` with `PORT` replaced | **Coming soon.** All ports are public. |
| `client.hosts.getUrl(port)` / `sdk.hosts.getUrl(token, port)` | `urlFormat.replace("PORT", String(port))` | **Coming soon.** |
| `sdk.hosts.createToken/listTokens/revokeToken/updateToken` | — | Not supported (no private previews). |
| `hosts.getHeaders/getCookies` | — | Not supported. |
| `csb preview-hosts` (allowed embedding hosts) | — | Not supported. |
| `createPreview()` iframe helper | — | Not supported. |

### CLI

| `csb` | `together-sandbox` |
| --- | --- |
| `csb build <dir> --alias a@b` | `together-sandbox snapshots create --context <dir> --alias a@b` |
| — | `together-sandbox snapshots list` / `snapshots get <id\|@alias>` |
| `csb sandboxes list` | `together-sandbox sandboxes list` (running only by default; `--all`) |
| `csb sandboxes fork <id>` | `sandboxes terminate <id> --snapshot-alias x` → `sandboxes create @x` |
| `csb sandboxes hibernate <id>` / `shutdown <id>` | `together-sandbox sandboxes terminate <id> [--snapshot-alias …]` |
| — | `together-sandbox sandboxes create <ref>` / `sandboxes get <id>` / `sandboxes run <ref> --rm -- cmd` |
| TUI dashboard terminal | `together-sandbox sandbox exec run <id> -it -- bash` |
| `csb host-tokens …` | — (not supported) |
| `csb preview-hosts …` | — (not supported) |
| `npx @codesandbox/sdk` | Install the binary with `install.sh` (the CLI is not on npm) |

## No longer supported

- Hibernate with memory, i.e. resuming with running processes intact
  (**coming soon** as memory snapshots).
- Resuming the *same* sandbox (same ID) after it stops.
- Live forks of a running sandbox that keep the parent running.
- Automatic wake-up on HTTP/WebSocket traffic (`automaticWakeupConfig`).
- Inactivity-based auto-hibernation (`hibernationTimeoutSeconds`,
  `updateHibernationTimeout`) — only absolute `ttl` from creation.
- Live resizing (`updateTier`); VM tiers above 16 vCPU / 32 GB (Large, XLarge).
- Privacy modes, private previews, host/preview tokens, preview-hosts
  allow-list, `createPreview` iframe helper.
- Sessions with read/write permissions, the browser and node clients
  (`connectToSandbox`), `disconnect`/`reconnect`/`keepActiveWhileConnected`.
- `.codesandbox/tasks.json` (setup tasks and tasks), `client.setup`,
  `client.tasks`, `restartOn`.
- Dev Container spec, Docker Compose auto-start, the default "Universal"
  template, importing existing CodeSandbox templates or sandboxes.
- `client.fs.download` zip URLs, `client.fs.batchWrite`.
- Interpreters with automatic last-expression return.
- Sandbox `title`/`description`/`path` metadata, `ipcountry`, custom IDs,
  list ordering, `listRunning` concurrency counts.
- OpenTelemetry `tracer` option, custom `fetch`/`headers`.
- CLI: `host-tokens`, `preview-hosts`, the interactive dashboard.

## Coming soon

| Feature | What to expect |
| --- | --- |
| Memory snapshots | Terminate with a disk + memory snapshot, so a new sandbox resumes with processes intact — the true equivalent of `hibernate`. Today `Snapshot.memory` is always `false`. |
| Preview URL template (`url_format`) | The sandbox model will carry a URL template such as `https://testsandbox-PORT.na-us-ce-01.cluster.csb.app`. Replace `PORT` with the port you want (e.g. `8080`). |
| Reattach by ID | A method to get a connected `Sandbox` for an already-running sandbox from its ID (name TBD). |

---

# Part 2 — Migration reference (for AI agents)

Follow the procedure in order. Every rule states the old pattern, the new
pattern, and behavioural differences you must account for. When the old code
relies on a feature listed in [No longer supported](#no-longer-supported),
do not invent a substitute: flag it to the user with a `TODO(migration)`
comment and describe the gap.

## 1. Detect old usage

Search the codebase for these patterns (regex, case-sensitive):

```
@codesandbox/sdk
CSB_API_KEY|CSB_BASE_URL
new CodeSandbox\(
\.sandboxes\.(create|resume|hibernate|shutdown|restart|fork|delete|list|listRunning|get)\(
\.connect\(|createSession\(|createBrowserSession\(|connectToSandbox\(|createPreview\(
\.(fs|commands|terminals|interpreters|tasks|setup|ports|hosts)\.
sdk\.hosts\.
VMTier
bootupType|isUpToDate
hibernationTimeoutSeconds|automaticWakeupConfig|updateTier|updateHibernationTimeout
keepActiveWhileConnected|disconnect\(|reconnect\(
CommandError|RateLimitError
csb (build|sandboxes|host-tokens|preview-hosts)|npx @codesandbox/sdk
\.codesandbox/(tasks\.json|Dockerfile)|\.devcontainer/
\.csb\.app|preview_token|csb-preview-token
/project/workspace|/project/sandbox
```

## 2. Procedure

1. **Dependencies and env.** Replace `@codesandbox/sdk` with `together-sandbox`
   (Node 18+) or add `together-sandbox` (Python 3.10+). Rename `CSB_API_KEY` →
   `TOGETHER_API_KEY` and `CSB_BASE_URL` → `TOGETHER_BASE_URL` in code, `.env`
   files, CI secrets and deployment manifests. The user must obtain a Together
   API key.
2. **Templates → snapshots.** For every template (`csb build` invocation or
   template ID in code), produce a Dockerfile (§4.4) and a
   `together-sandbox snapshots create` step with an alias. Replace template IDs
   in code with the alias.
3. **Client construction** (§4.1).
4. **Sandbox creation and lifecycle** (§4.2, §4.3). Wherever the app stores a
   sandbox ID across a hibernate/resume cycle, change it to store either the
   latest sandbox ID *and* the snapshot alias it was terminated to, or just the
   alias. Add `terminationPolicy` wherever state must survive.
5. **Remove `connect()` / sessions** (§4.5, §4.10). Use the `Sandbox` returned by
   `create()` directly.
6. **In-VM operations** (§4.6 – §4.9).
7. **Tasks and setup** (§4.4). Move setup into the Dockerfile; start
   long-running processes with `execs.create` after every create.
8. **Previews** (§4.9).
9. **Errors and retries** (§4.11).
10. **CLI scripts** (§4.12).
11. **Delete dead code** for unsupported features, leaving `TODO(migration)`
    notes where behaviour is lost.
12. Run the [checklist](#5-checklist).

## 3. Key semantic differences (read before rewriting)

- **Termination is final.** `terminate()` tears the VM down. To continue,
  create a new sandbox from the snapshot. There is no way to start a terminated
  sandbox again.
- **The produced snapshot is aliased `sandbox:<sandboxId>`.** Additional aliases
  can be set in `terminationPolicy.snapshot.aliases` (at create) or in
  `terminate({ snapshot: { aliases } })` (overrides the stored policy for that
  teardown).
- **`terminate()` without options uses the stored policy.** If the sandbox was
  created without `terminationPolicy` it is ephemeral and nothing is kept.
  `terminate({ snapshot: null })` forces an ephemeral teardown.
- **Disk only.** Only the filesystem is snapshotted. Processes, open ports and
  in-memory state are lost. After every create, re-run whatever the app needs
  running (the old `bootupType === "CLEAN"` branch is now the only branch).
- **The whole filesystem is snapshotted**, not just `/project/workspace`, and
  `.gitignore` is not honoured. There is no `/project/workspace` convention;
  the working directory is whatever your Dockerfile sets (`WORKDIR`). Use
  absolute paths everywhere — there is no workspace-relative path resolution.
- **`create()` blocks until `running`** and throws if the sandbox reaches
  `failed_to_start`. `terminate()` blocks until `terminated`.
- **Default exec user.** Execs run as the server default (UID/GID 1000 unless
  the image says otherwise), not root. Pass `user: "root"` (or `"0:0"`) when
  you need root.
- **`execs.exec` does not throw on non-zero exit.** Check `exitCode`. (Old
  `commands.run` threw `CommandError`.)
- **Python is async only.** Use `await` and `async with`; exiting
  `async with sandbox` closes HTTP connections but does not terminate the VM.

## 4. Rewrite rules

TypeScript is shown first; the Python equivalent follows each rule. Python
names are snake_case (`snapshot_alias`, `termination_policy`, `memory_bytes`,
`exit_code`, `retire_by_id`, `get_by_alias`).

### 4.1 Client

```typescript
// Before
import { CodeSandbox } from "@codesandbox/sdk";
const sdk = new CodeSandbox(process.env.CSB_API_KEY);

// After
import { TogetherSandbox } from "together-sandbox";
const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY! });
```

```python
from together_sandbox import TogetherSandbox

sdk = TogetherSandbox()  # reads TOGETHER_API_KEY
# ... or: async with TogetherSandbox() as sdk: ...
```

- `opts.baseUrl` → `baseUrl` (or `TOGETHER_BASE_URL`).
- `opts.tracer`, `opts.fetch`, `opts.headers` → remove; add a
  `TODO(migration)` if tracing was relied on.
- Retries: see §4.11.

### 4.2 Creating sandboxes

```typescript
// Before
const sandbox = await sdk.sandboxes.create({
  id: "my-template@v1",
  title: "User 42 workspace",
  tags: ["user-42"],
  privacy: "private",
  vmTier: VMTier.Micro,
  hibernationTimeoutSeconds: 3600,
  automaticWakeupConfig: { http: true, websocket: false },
});
const client = await sandbox.connect();

// After
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-template@v1",
  tags: { title: "user-42-workspace", user: "42" },
  cpu: 4,
  memoryBytes: 8 * 1024 ** 3,
  ttl: 3600, // absolute seconds since creation, not idle time
  terminationPolicy: { snapshot: { aliases: ["user-42@latest"] } },
});
// `sandbox` is already connected: sandbox.files, sandbox.execs, ...
```

```python
sandbox = await sdk.sandboxes.create(
    snapshot_alias="my-template@v1",
    tags={"title": "user-42-workspace", "user": "42"},
    cpu=4,
    memory_bytes=8 * 1024**3,
    ttl=3600,
    termination_policy={"snapshot": {"aliases": ["user-42@latest"]}},
)
```

Option mapping:

| Old option | New option | Rule |
| --- | --- | --- |
| `id` (template / sandbox / `ns@alias`) | `snapshotAlias` or `snapshotId` | Required. A sandbox ID is not accepted; use `sandbox:<id>` as the alias. |
| omitted `id` (Universal template) | — | Must specify a snapshot. |
| `vmTier` | `cpu`, `memoryBytes` | See table below. Default is 1 vCPU / 2 GiB. |
| `hibernationTimeoutSeconds` | `ttl` + `terminationPolicy` | Semantics differ (absolute vs idle). If the app relied on idle timeout, implement activity tracking and call `terminate`. |
| `automaticWakeupConfig` | — | Remove. |
| `tags: string[]` | `tags: Record<string,string>` | e.g. `["a","b"]` → `{ a: "true", b: "true" }`. Keys ≤ 59 chars of `[A-Za-z0-9-_.]`, start/end alphanumeric. |
| `title`, `description`, `path` | `tags` | Optional; values must be strings. |
| `privacy` | — | Remove. All ports are public. |
| `ipcountry` | — | Remove. |
| — | `terminationPolicy` | **Add** if the sandbox's filesystem must survive termination. |

#### VM tiers → `cpu` / `memoryBytes`

Limits: `cpu` 0.1–16, `memoryBytes` between 1 and 8 GB per CPU, max
32,000,000,000 bytes. Disk size is not configurable.

| Old `VMTier` | Old specs | New params |
| --- | --- | --- |
| `Pico` | 1 vCPU, 2 GiB | `cpu: 1, memoryBytes: 2 * 1024 ** 3` (default) |
| `Nano` | 2 vCPU, 4 GiB | `cpu: 2, memoryBytes: 4 * 1024 ** 3` |
| `Micro` | 4 vCPU, 8 GiB | `cpu: 4, memoryBytes: 8 * 1024 ** 3` |
| `Small` | 8 vCPU, 16 GiB | `cpu: 8, memoryBytes: 16 * 1024 ** 3` |
| `Medium` | 16 vCPU, 32 GiB | `cpu: 16, memoryBytes: 32_000_000_000` (max) |
| `Large` | 32 vCPU, 64 GiB | Not supported — cap at `Medium` values and flag. |
| `XLarge` | 64 vCPU, 128 GiB | Not supported — cap at `Medium` values and flag. |

`VMTier.fromSpecs({ cpu, memGiB })` → pass `cpu` and
`memoryBytes: memGiB * 1024 ** 3` directly.

### 4.3 Lifecycle recipes

#### Hibernate / shutdown → terminate with snapshot

```typescript
// Before
await sdk.sandboxes.hibernate(sandboxId);
// or
await sdk.sandboxes.shutdown(sandboxId);

// After (disk-only snapshot; memory snapshots coming soon)
await sdk.sandboxes.terminate(sandboxId, {
  snapshot: { aliases: ["user-42@latest"] },
});
// or, with the Sandbox object:
await sandbox.terminate({ snapshot: { aliases: ["user-42@latest"] } });
```

```python
await sdk.sandboxes.terminate(sandbox_id, snapshot={"aliases": ["user-42@latest"]})
```

If the sandbox was created with a `terminationPolicy`, a plain
`terminate()` applies it. Choose one place (create-time policy or
terminate-time override) and be consistent.

#### Resume → create from snapshot

```typescript
// Before
const sandbox = await sdk.sandboxes.resume(sandboxId); // same ID
if (sandbox.bootupType === "CLEAN") {
  /* re-run setup */
}

// After
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: `sandbox:${previousSandboxId}`, // or "user-42@latest"
  terminationPolicy: { snapshot: { aliases: ["user-42@latest"] } },
});
await db.saveSandboxId(userId, sandbox.id); // NEW ID — persist it
await startProcesses(sandbox); // always: processes do not survive
```

```python
sandbox = await sdk.sandboxes.create(
    snapshot_alias=f"sandbox:{previous_sandbox_id}",
    termination_policy={"snapshot": {"aliases": ["user-42@latest"]}},
)
```

Prefer a stable, per-entity alias (`user-42@latest`) re-applied on each
termination: the app then only needs the alias, not a chain of IDs. Aliases are
mutable, so each termination moves the pointer to the newest snapshot.

Old `resume()` was also used to *wake* a sandbox that was still running.
If the sandbox is still `running`, do not create a new one — reuse the live
`Sandbox` object (see [Reattaching](#reattaching-to-a-running-sandbox)). Check
with `sdk.sandboxes.get(id)` → `info.status`.

#### Restart

```typescript
// Before
const sandbox = await sdk.sandboxes.restart(sandboxId, { vmTier: VMTier.Small });

// After
await sdk.sandboxes.terminate(sandboxId, { snapshot: { aliases: [] } });
const restarted = await sdk.sandboxes.create({
  snapshotAlias: `sandbox:${sandboxId}`,
  cpu: 8,
  memoryBytes: 16 * 1024 ** 3,
});
```

This is also how you **resize** (old `updateTier`). Remove any
`isUpToDate` → `restart` logic; it is not needed.

#### Delete

```typescript
// Before
await sdk.sandboxes.delete(sandboxId);

// After
await sdk.sandboxes.terminate(sandboxId, { snapshot: null }); // no snapshot kept
// And, to free snapshots you created earlier:
await sdk.snapshots.retire(snapshotId);
```

```python
await sdk.sandboxes.terminate(sandbox_id, snapshot=None)
await sdk.snapshots.retire_by_id(snapshot_id)
```

A retired snapshot can no longer start sandboxes and is deleted once nothing
references it. Snapshot lifetime can also be bounded up front with
`terminationPolicy.snapshot.ttl` (seconds).

#### Fork / live fork

```typescript
// Before
const child = await sdk.sandboxes.create({ id: parentSandboxId }); // parent keeps running

// After — the parent stops
await sdk.sandboxes.terminate(parentId, { snapshot: { aliases: ["exp@base"] } });
const children = await Promise.all(
  [1, 2, 3].map(() => sdk.sandboxes.create({ snapshotAlias: "exp@base" })),
);
// If the parent must keep working, create a replacement from the same snapshot:
const parent = await sdk.sandboxes.create({ snapshotAlias: "exp@base" });
```

Forking a template (`create({ id: templateId })`) is just
`create({ snapshotAlias })`.

#### Idle timeout / auto-hibernate

There is no idle detection. Options, in order of preference:

1. Track activity in your backend (last request per sandbox) and call
   `terminate({ snapshot })` after your idle window.
2. Set `ttl` at create as an upper bound. When it elapses the sandbox is
   terminated (`statusReason: "autoterminated"`) and its `terminationPolicy`
   applies — so combine `ttl` with `terminationPolicy` to keep the filesystem.

#### Boot type → status reason

`sandbox.bootupType` has no equivalent. `sandbox.vmInfo.status` /
`statusReason` tell you the state (`running` / `cold_started` or `restored`).
Treat every newly created sandbox as a clean boot and run your startup steps.

#### Reattaching to a running sandbox

Old stateless backends did `resume(id)` + `connect()` on every request. A
method to reattach by ID is **coming soon**. Until then:

- Keep the `Sandbox` object in memory (e.g. a `Map<string, Sandbox>` in the
  process that created it) for the sandbox's lifetime; or
- As a stopgap, rebuild a `Sandbox` from its metadata. `agent.token` is a
  secret — keep this server-side:

```typescript
import {
  Sandbox,
  TogetherSandbox,
  createApiClient,
  createApiConfig,
  createSandboxClient,
  createSandboxConfig,
} from "together-sandbox";

async function reattach(sdk: TogetherSandbox, id: string): Promise<Sandbox> {
  const info = await sdk.sandboxes.get(id);
  if (info.status !== "running" || !info.agent?.url || !info.agent?.token) {
    throw new Error(`sandbox ${id} is ${info.status}`);
  }
  const sandboxClient = createSandboxClient(
    createSandboxConfig({
      baseUrl: info.agent.url,
      headers: { Authorization: `Bearer ${info.agent.token}` },
    }),
  );
  const apiClient = createApiClient(
    createApiConfig({
      baseUrl: `${process.env.TOGETHER_BASE_URL ?? "https://api.bartender.codesandbox.io"}/v1`,
      headers: { Authorization: `Bearer ${process.env.TOGETHER_API_KEY}` },
    }),
  );
  return new Sandbox(info, sandboxClient, apiClient);
}
```

Replace this helper with the official method once it ships.

#### Listing

```typescript
// Before
const { sandboxes } = await sdk.sandboxes.list({ tags: ["user-42"], status: "running" });
const running = await sdk.sandboxes.listRunning();

// After
for await (const info of await sdk.sandboxes.list({
  tags: { user: "42" },
  statuses: ["running"],
})) {
  console.log(info.id, info.status, info.statusReason);
}
```

```python
async for info in await sdk.sandboxes.list(tags={"user": "42"}, statuses=["running"]):
    print(info.id, info.status)
```

- `limit`/`pagination` → `limit` (1–100 per page) + `cursor`; the returned
  `Page` is async-iterable across pages, or use `hasNextPage()` /
  `getNextPage()`.
- `orderBy`, `direction` → not supported; sort client-side.
- `listRunning().concurrentVmCount/Limit` → not exposed.
- New filter: `snapshotId` (sandboxes created from a given snapshot).

### 4.4 Templates, tasks and setup → snapshots

```bash
# Before
npx @codesandbox/sdk build ./my-template --ports 5173 --vm-tier Micro --alias my-template@v1

# After
together-sandbox snapshots create --context ./my-template --alias my-template@v1 --cache-key my-template
```

```typescript
// SDK equivalent
const { snapshotId, alias } = await sdk.snapshots.create({
  context: "./my-template",
  alias: "my-template@v1",
  cacheKey: "my-template",
  onProgress: (e) => console.log(e.step, e.output),
});
```

Converting a CodeSandbox template directory:

1. If it has `.codesandbox/Dockerfile`, move it to `Dockerfile` (or pass
   `--dockerfile`). If it has `.devcontainer/devcontainer.json` with `image`,
   write `FROM <image>`; with `build.dockerfile`, use that Dockerfile. Dev
   Container `features` and `dockerComposeFile` must be translated into
   Dockerfile steps by hand. The old requirement for `zsh` in the image no
   longer applies.
2. Add `COPY` / `WORKDIR` for the project files. Old templates uploaded the
   directory into `/project/workspace`; now only what the Dockerfile copies is
   present. Choose a path (e.g. `/workspace`) and use it consistently in code.
3. Move each `setupTasks` entry (dependency installs, builds) into a `RUN`
   step. Anything that needs runtime data (secrets, user repos) becomes an
   `execs.exec` call after `create`.
4. Each `tasks` entry (dev servers, watchers) becomes an `execs.create` call
   after every `create` (see §4.7). `runAtStart: true` means "call it in your
   startup routine". `restartOn` has no equivalent (use `nodemon`/`chokidar`
   inside the command).
5. `--ports` waits and `--vm-tier` / `--vm-build-tier` are dropped. Size is
   chosen per sandbox at `create`.
6. Delete `.codesandbox/tasks.json` once converted.

Alias management: `sdk.snapshots.alias(snapshotId, "my-template@v2")`,
`sdk.snapshots.getByAlias(alias)`, `sdk.snapshots.getById(id)`,
`sdk.snapshots.list({ excludeRetired, tags })`, `sdk.snapshots.retire(id)`
(Python: `retire_by_id`). Aliases are `tag` or `namespace@tag` and can be
repointed at any time — use them for rollouts (`my-app@latest`).

A snapshot's filesystem can also come from a running sandbox: terminate it with
`snapshot: { aliases: ["my-template@v2"] }`. This replaces the old
`csb build --from-sandbox` / "hibernated sandbox as template" pattern.

### 4.5 Connecting, sessions and users

```typescript
// Before
const client = await sandbox.connect({
  id: "user-42",
  permission: "write",
  env: { API_URL: "https://example.com" },
  git: { provider: "github.com", accessToken: token, email: "a@b.c", name: "A" },
});
await client.commands.run("git clone https://github.com/org/repo");

// After — create the user once (or bake it into the Dockerfile with RUN useradd)
await sandbox.execs.exec("useradd", ["-m", "user42"], { user: "root" });

await sandbox.execs.exec(
  "bash",
  [
    "-lc",
    'git config --global user.email "a@b.c" && git config --global user.name "A" && ' +
      'git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/org/repo" /home/user42/repo',
  ],
  {
    user: "user42",
    env: { GITHUB_TOKEN: token, API_URL: "https://example.com" },
  },
);
```

```python
await sandbox.execs.exec("useradd", ["-m", "user42"], user="root")
await sandbox.execs.exec(
    "bash",
    ["-lc", 'git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/org/repo" /home/user42/repo'],
    user="user42",
    env={"GITHUB_TOKEN": token},
)
```

- `connect()`, `createSession()`, `createBrowserSession()` → remove; use the
  `Sandbox` from `create()`.
- Session `id` → exec `user` (`"name"`, `"uid"`, `"uid:gid"`, `"name:group"`).
- Session `env` → exec `env` on each call (it is not persisted between execs;
  write a file in the image or home directory if you need persistent env).
- Session `git` → env vars + git commands as above. Never write tokens into
  the snapshot unless you intend them to persist.
- `permission: "read"` → no equivalent; flag it.
- `client.disconnect()`, `reconnect()`, `keepActiveWhileConnected()`,
  `onStateChange`, `dispose()` → remove. There is no persistent connection.

### 4.6 Filesystem

```typescript
// Before
await client.fs.writeTextFile("index.js", "console.log(1)");
const text = await client.fs.readTextFile("index.js");
const entries = await client.fs.readdir(".");
await client.fs.mkdir("src/utils", true);
await client.fs.rename("a.txt", "b.txt");
await client.fs.copy("b.txt", "c.txt");
await client.fs.remove("tmp", true);
const st = await client.fs.stat("b.txt");
const watcher = await client.fs.watch("src", { recursive: true, excludes: ["node_modules"] });
watcher.onEvent((e) => console.log(e.type, e.paths));

// After — absolute paths
await sandbox.files.create("/workspace/index.js", "console.log(1)");
const text2 = await sandbox.files.read("/workspace/index.js");
const entries2 = await sandbox.directories.list("/workspace");
await sandbox.directories.create("/workspace/src/utils");
await sandbox.files.move("/workspace/a.txt", "/workspace/b.txt");
await sandbox.files.copy("/workspace/b.txt", "/workspace/c.txt");
await sandbox.directories.delete("/workspace/tmp");
const st2 = await sandbox.files.stat("/workspace/b.txt"); // { name, path, isDir, size, modTime }
const stream = await sandbox.files.watch("/workspace/src", {
  recursive: true,
  ignorePatterns: ["node_modules/**"],
});
// `stream` is an SSE ReadableStream of { paths, type: "ADD" | "REMOVE" | "CHANGE", timestamp }
```

Python: `files.create(path, str | bytes)`, `files.read`, `files.move(from_path,
to_path)`, `files.copy`, `files.delete`, `files.stat`,
`directories.list/create/delete`, and
`async for event in sandbox.files.watch(path, recursive=True, ignore_patterns=[...])`.

Differences:

- Relative paths were resolved against `/project/workspace`; now always pass
  absolute paths.
- `readFile` (binary, `Uint8Array`) → `files.read` returns a string; binary
  content comes back base64-encoded. Decode it (`Buffer.from(s, "base64")`)
  or, to be safe, read binaries via `execs.exec("base64", ["-w0", path])`.
- `writeFile(path, Uint8Array)` → `files.create(path, new Blob([bytes]))`
  (TS) / `files.create(path, b"...")` (Python).
- `writeFile` `create`/`overwrite` options → `files.create` always creates or
  overwrites.
- `readdir` entries `{ name, type, isSymlink }` → `FileInfo { name, path,
  isDir, size, modTime }`.
- `stat` `{ type, isSymlink, size, mtime, ctime, atime }` → `{ name, path,
  isDir, size, modTime }`.
- `mkdir(path, recursive)` → `directories.create` (creates parents).
- `remove(path, recursive)` → `files.delete` for files,
  `directories.delete` for directories.
- `rename(from, to, overwrite)` / `copy(from, to, recursive, overwrite)` →
  `files.move` / `files.copy` (no flags).
- Watch events are uppercase (`ADD`/`REMOVE`/`CHANGE`); `watcher.dispose()` →
  cancel the stream / break the loop.
- `batchWrite(files)` → loop `files.create`, or upload one tarball with
  `files.create("/tmp/b.tar", blob)` and `execs.exec("tar", ["-xf",
  "/tmp/b.tar", "-C", "/workspace"])`.
- `download(path)` (5-minute zip URL) → not supported. Run
  `execs.exec("bash", ["-lc", "cd /workspace && tar -czf /tmp/out.tgz . && base64 -w0 /tmp/out.tgz"])`
  and decode the output, or push to your own storage from inside the sandbox.

### 4.7 Commands, terminals and interpreters → execs

#### Foreground command

```typescript
// Before
try {
  const out = await client.commands.run("npm test", { cwd: "/project/workspace", env: { CI: "1" } });
} catch (e) {
  if (e instanceof CommandError) console.log(e.exitCode, e.output);
}

// After
const { exitCode, output } = await sandbox.execs.exec("bash", ["-lc", "npm test"], {
  cwd: "/workspace",
  env: { CI: "1" },
});
if (exitCode !== 0) console.log(exitCode, output);
```

```python
result = await sandbox.execs.exec("bash", ["-lc", "npm test"], cwd="/workspace", env={"CI": "1"})
if result["exit_code"] != 0:
    print(result["output"])
```

- A string command → `("bash", ["-lc", cmd])`. A command array (old SDK joined
  with `&&`) → `("bash", ["-lc", cmds.join(" && ")])`, or pass
  `command` + `args` directly when it is a single program.
- `output` is stdout + stderr interleaved (same as old). Use `getOutput` /
  `streamOutput` for per-chunk `type: "stdout" | "stderr"`.
- `asGlobalSession`, `name`, `dimensions` → drop (`pty: true` for a TTY).

#### Background command / task

```typescript
// Before
const cmd = await client.commands.runBackground("npm run dev", { name: "dev" });
cmd.onOutput((o) => console.log(o));
await client.ports.waitForPort(3000);
await cmd.kill();

// After
const exec = await sandbox.execs.create({
  command: "bash",
  args: ["-lc", "npm run dev"],
  cwd: "/workspace",
  autostart: true,
});
const out = await sandbox.execs.streamOutput(exec.id); // SSE stream of ExecStdout
await waitForPort(sandbox, 3000); // helper in §4.9
await sandbox.execs.delete(exec.id); // stops it
```

```python
exec_ = await sandbox.execs.create("bash", ["-lc", "npm run dev"], cwd="/workspace")
async for chunk in sandbox.execs.stream_output(exec_.id):
    print(chunk)
await sandbox.execs.delete(exec_.id)
```

- `command.open()` / `onOutput` → `execs.streamOutput(id, lastSequence?)` or
  poll `execs.getOutput(id)`.
- `command.waitUntilComplete()` → poll `execs.getOutput(id)` until `exitCode`
  is defined, or use `execs.exec` for commands that should block.
- `command.kill()` → `execs.delete(id)`.
- `command.restart()` → delete and create again.
- `client.commands.getAll()` → `execs.list()`; live updates via
  `execs.streamList()`.
- `task.run/stop/restart`, `task.waitForPort` → the same exec calls plus the
  port helper.

#### Terminals

```typescript
// Before
const term = await client.terminals.create("bash");
term.onOutput((d) => ui.write(d));
await term.open();
await term.write("ls\n");

// After
const t = await sandbox.execs.create({ command: "bash", args: ["-l"], pty: true });
const tStream = await sandbox.execs.streamOutput(t.id);
await sandbox.execs.sendStdin(t.id, { type: "stdin", input: "ls\n" });
await sandbox.execs.sendStdin(t.id, { type: "resize", input: "120x40" }); // cols x rows
await sandbox.execs.delete(t.id); // was term.kill()
```

Python: `await sandbox.execs.send_stdin(id, "ls\n")`,
`await sandbox.execs.resize(id, cols=120, rows=40)`.

`client.terminals.getAll()` → `execs.list()` (filter `pty`). For an interactive
shell from a terminal, use `together-sandbox sandbox exec run <id> -it -- bash`.

#### Interpreters

```typescript
// Before
const r1 = await client.interpreters.javascript("1 + 1"); // "2"
const r2 = await client.interpreters.python("1 + 1"); // "2"

// After — no automatic last-expression return; print explicitly
const js = await sandbox.execs.exec("node", ["-e", "console.log(1 + 1)"]);
const py = await sandbox.execs.exec("python3", ["-c", "print(1 + 1)"]);
```

The image must contain `node` / `python3`.

### 4.8 Setup progress

`client.setup.getSteps()`, `client.setup.waitUntilComplete()`,
`onSetupProgressChange` → remove. Build-time setup happens during
`snapshots.create` (observe it with `onProgress`); run-time setup is your own
sequence of `execs.exec` calls after `create`, whose results you check
directly.

### 4.9 Ports and preview URLs

```typescript
// Before
const port = await client.ports.waitForPort(3000);
const url = client.hosts.getUrl(3000); // https://<id>-3000.csb.app[?preview_token=…]

// After
async function waitForPort(sb: Sandbox, port: number, timeoutMs = 60_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const ports = await sb.ports.list();
    const found = ports.find((p) => p.port === port);
    if (found) return found; // { port, address }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`port ${port} did not open within ${timeoutMs} ms`);
}
await waitForPort(sandbox, 3000);

// Preview URL — COMING SOON: the sandbox model will expose `url_format`
// (e.g. "https://testsandbox-PORT.na-us-ce-01.cluster.csb.app").
// const previewUrl = urlFormat.replace("PORT", String(3000));
```

- `client.ports.getAll()` / `get(port)` → `sandbox.ports.list()` (`{ port,
  address }`, where `address` is the bind address, not a URL).
- `onDidPortOpen` / `onDidPortClose` → `sandbox.ports.streamList()` (SSE).
- `client.hosts.getUrl(port)`, `sdk.hosts.getUrl(token, port)` → replace
  `PORT` in the sandbox's `url_format` (coming soon). Until it ships, leave a
  `TODO(migration)`.
- All ports are public. `privacy: "private"`, host tokens
  (`sdk.hosts.createToken/listTokens/revokeToken/revokeAllTokens/updateToken`),
  `getHeaders`, `getCookies`, `preview_token` query parameters and the
  `csb_is_trusted` cookie → remove. If previews must be private, put your own
  authenticating proxy in front and do not share the raw URL.
- `createPreview()` and the preview message protocol → not supported; embed the
  URL in your own iframe.
- Auto-wake on HTTP → not supported: a request to a terminated sandbox does
  not start it. Your backend must create the sandbox before handing out the
  URL.

### 4.10 Browser and Node clients

`@codesandbox/sdk/browser` and `@codesandbox/sdk/node` (`connectToSandbox`,
`getSession`, `onFocusChange`) are not supported, and calling the in-VM API
from a browser is not recommended: `agent.token` is a secret for the sandbox.
Instead, expose your own backend endpoints (e.g. `POST /api/sandboxes/:id/files`,
`POST /api/sandboxes/:id/exec`, an SSE endpoint that relays
`execs.streamOutput`) that use the SDK server-side, and call those from the
browser.

### 4.11 Errors and retries

```typescript
import { HttpError } from "together-sandbox";

try {
  await sdk.sandboxes.get(id);
} catch (e) {
  if (e instanceof HttpError) {
    if (e.status === 0) {
      /* transport failure */
    } else if (e.status === 404) {
      /* not found */
    } else if (e.status === 429) {
      /* rate limited (old RateLimitError) */
    }
  }
  throw e;
}
```

- `RateLimitError`, `"Sandbox not found"` / `"Unauthorized"` string errors →
  `HttpError` with `status` (0 = transport-level failure), `code`, `hint`.
- `CommandError` → check `exitCode` from `execs.exec`.
- The SDK retries 408/429/5xx and transport failures automatically (3 attempts,
  exponential backoff). Remove hand-written retry loops around SDK calls, or
  configure `retry: { maxAttempts, shouldRetry, onRetry }`. Exclude
  `snapshots.create` from retries (not idempotent):
  `shouldRetry: ({ operation }) => operation !== "snapshots.create"`.
- `create()` throws if the sandbox ends in `failed_to_start`
  (`statusReason: out_of_capacity | internal_error`); handle it like the old
  503 "overloaded" error.

### 4.12 CLI

| Old | New |
| --- | --- |
| `CSB_API_KEY=… csb …` | `TOGETHER_API_KEY=… together-sandbox …` |
| `csb build ./dir --alias ns@v1 [--ci]` | `together-sandbox snapshots create --context ./dir --alias ns@v1 [--ci]` |
| `csb sandboxes list -t tag -s running` | `together-sandbox sandboxes list --tag k=v` (running by default; `--all`, `--status`) |
| `csb sandboxes list -o id,…` | `together-sandbox sandboxes list -o json` |
| `csb sandboxes fork <id>` | `together-sandbox sandboxes terminate <id> --snapshot-alias ns@x && together-sandbox sandboxes create @ns@x` |
| `csb sandboxes hibernate <id>` / `shutdown <id>` | `together-sandbox sandboxes terminate <id> --snapshot-alias ns@x` |
| resume (dashboard) | `together-sandbox sandboxes create @sandbox:<id>` |
| delete | `together-sandbox sandboxes terminate <id> --ephemeral` |
| dashboard terminal | `together-sandbox sandbox exec run <id> -it -- bash` |
| `csb host-tokens …`, `csb preview-hosts …` | Remove (not supported). |

`sandboxes create` flags: `--cpu`, `--memory-bytes`, `--ttl`, `--tag K=V`,
`--snapshot-on-terminate`, `--snapshot-alias`, `--snapshot-ttl`. Without
`--snapshot-on-terminate` the sandbox is ephemeral. Install the CLI with
`curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash`
(it is not published to npm). See [CLI](./cli.md).

## 5. Checklist

- [ ] No imports of `@codesandbox/sdk` remain; `together-sandbox` is installed.
- [ ] `CSB_API_KEY` / `CSB_BASE_URL` replaced everywhere (code, env files, CI).
- [ ] Every template has a Dockerfile and a `snapshots create` step with an
      alias; code references the alias.
- [ ] `.codesandbox/tasks.json` setup tasks moved to Dockerfile `RUN` steps;
      tasks started with `execs.create` after every `create`.
- [ ] Every `create` passes `snapshotAlias`/`snapshotId`, explicit `cpu` /
      `memoryBytes` if not default, and `terminationPolicy` where state must
      persist.
- [ ] `hibernate` / `shutdown` → `terminate({ snapshot })`; `resume` /
      `restart` / `fork` → `create` from `sandbox:<id>` or an alias; the new
      sandbox ID is persisted.
- [ ] Startup processes are re-run after every create (no reliance on
      `bootupType` or surviving processes).
- [ ] `connect()`, sessions, `disconnect`, `keepActiveWhileConnected` removed.
- [ ] All paths are absolute; no reliance on `/project/workspace`.
- [ ] `commands.run` callers check `exitCode` instead of catching
      `CommandError`.
- [ ] Preview URL code is marked `TODO(migration)` for `url_format`; host
      tokens and privacy handling removed.
- [ ] No browser code talks to the sandbox directly; `agent.token` never leaves
      the backend.
- [ ] Custom retry loops removed or replaced by `RetryConfig`.
- [ ] Every unsupported feature the app depended on is listed for the user.

See also: [Sandboxes & Snapshots](./sandboxes.md),
[TypeScript SDK](https://github.com/togethercomputer/together-sandbox/blob/main/docs/typescript-sdk.md),
[Python SDK](https://github.com/togethercomputer/together-sandbox/blob/main/docs/python-sdk.md),
[CLI](./cli.md).

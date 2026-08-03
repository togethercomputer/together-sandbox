# Sandboxes & Snapshots

This document explains the core concepts behind Together Sandbox: what sandboxes and snapshots are, how their lifecycles work, and how they relate to each other.

---

## What is a sandbox?

A sandbox is a virtual machine that runs on Together's infrastructure. You create one — it starts automatically — run code inside it (via shell commands, file operations, and port forwarding), then terminate it. When a sandbox terminates it snapshots its filesystem; to carry that filesystem forward you create a new sandbox from the produced snapshot. Once terminated, a sandbox cannot be used again. Sandboxes can optionally be created as **ephemeral**, in which case they take no snapshot and are automatically deleted when they terminate.

Every sandbox is backed by a **snapshot**.

---

## What is a snapshot?

A snapshot is a compressed, immutable disk image stored in Together's registry. It defines the filesystem that a sandbox starts from.

Snapshots are created from Docker images — either by building from a Dockerfile or by referencing an existing image. Once registered, a snapshot can be used to start any number of sandboxes. They are also automatically generated when you terminate a sandbox.

Snapshots can be addressed by:

- **UUID** — the snapshot's permanent unique identifier, e.g. `a1b2c3d4-…`
- **Alias** — a human-readable name you assign, e.g. `my-app@v1` or `latest`

---

## Sandbox lifecycle

A sandbox moves through the following states:

```
                 create()
                    │
                    ▼
              ┌──────────┐
              │ starting │  ← transitional
              └────┬─────┘
                   │
                   ▼
              ┌─────────┐
              │ running │  ◄─── you interact with the sandbox here
              └────┬────┘
                   │ terminate()
                   ▼
              ┌─────────────┐
              │ terminating │  ← transitional
              └──────┬──────┘
                   │
                   ▼
              ┌────────────┐
              │ terminated │  ← terminal; create a new sandbox from a snapshot to continue
              └────────────┘
```

Sandboxes autostart on creation. `starting` and `terminating` are transient states — `create()` and `terminate()` both block until the sandbox reaches a terminal state (`running` or `terminated`). Once a sandbox reaches `terminated` it cannot be used again. To continue from a terminated sandbox's state, create a new sandbox from the snapshot it produced.

**Note!** A `starting` sandbox that cannot start moves to `failed_to_start` (terminal). If a running sandbox crashes it is auto-recovered (`recovering`); if recovery fails it ends in `unrecovered`.

The `status_reason` field always records why the sandbox is in its current status — including while `starting` (`cold_start_requested`) and `running` (`cold_started` / `restored`).

### Failed-to-start reasons

When a sandbox reaches the `failed_to_start` state, `status_reason` records why:

| Reason             | Description                                        |
| ------------------ | -------------------------------------------------- |
| `out_of_capacity`  | No capacity was available to start the sandbox     |
| `internal_error`   | The sandbox failed to reach the `running` state    |

### Termination reasons

When a sandbox reaches the `terminated` state, the `status_reason` field records why:

| Reason                  | Description                                               |
| ----------------------- | --------------------------------------------------------- |
| `termination_requested` | A client called the terminate API                         |
| `autoterminated`        | The sandbox was terminated automatically (its TTL elapsed)|
| `crashed`               | The VM process exited unexpectedly                        |
| `oom_killed`            | The sandbox ran out of memory                             |
| `evicted`               | Removed by the cluster scheduler (e.g. resource pressure) |
| `node_lost`             | The node running the sandbox became unavailable           |
| `cluster_lost`          | The cluster running the sandbox became unavailable        |

---

## Terminating

Terminating a sandbox tears it down for good. `terminate()` takes a
`snapshot` object `{ aliases, ttl, tags }` selecting which aliases and tags to
apply to the snapshot taken on teardown. Omit it to use the policy the sandbox
was created with, or pass `null` to make the teardown ephemeral (no snapshot).

```typescript
await sandbox.terminate({ snapshot: { aliases: ["my-app@v2"] } });
```

The VM is torn down cleanly and its filesystem is snapshotted. A new sandbox created from the resulting snapshot boots from disk with a clean slate — no in-memory state is carried over.

---

## Source and result snapshots

- `snapshot_id` — the snapshot the sandbox booted from (set at creation).
- The snapshot created when the sandbox terminates
  is **not** stored on the sandbox model. It is aliased as `sandbox:<sandbox id>`,
  so you can create a new sandbox from it with `snapshotAlias: "sandbox:<id>"`.

To continue from a terminated sandbox, create a new sandbox from its produced snapshot (`snapshotAlias: "sandbox:<id>"`). This is how you "resume" work — useful for branching or rollback — since a terminated sandbox cannot be used again.

---

## Snapshots in depth

### Creating an initial snapshot

Initial snapshots are created from a Docker image. There are two paths:

**From a Dockerfile (build context):**

The SDK (or CLI) builds a Docker image, authenticates with Together's container registry, pushes the image, and registers the snapshot. The build can happen remotely (default) or locally via `TOGETHER_LOCAL_BUILD=1`.

```typescript
const result = await sdk.snapshots.create({
  context: "./my-app", // path to build context
  dockerfile: "./my-app/Dockerfile.prod", // optional, defaults to context/Dockerfile
  alias: "my-app@v1", // optional alias
  onProgress: (event) => console.log(event.step, event.output),
});
```

**From an existing image:**

If you already have a Docker image (public or in a registry you can access), you can create a snapshot directly from it:

```typescript
const result = await sdk.snapshots.create({
  image: "python:3.12-slim",
  alias: "my-python@latest",
});
```

### Snapshot creation steps

The progress `step` field cycles through these stages:

| Step       | What's happening                                   |
| ---------- | -------------------------------------------------- |
| `prepare`  | Validating inputs, setting up build context        |
| `build`    | Building the Docker image (context-based only)     |
| `auth`     | Issuing registry credentials and authenticating    |
| `push`     | Pushing the image to Together's container registry |
| `register` | Registering the snapshot in the management API     |
| `alias`    | Assigning the alias to the snapshot                |

### Snapshot properties

| Field                      | Type             | Description                                                       |
| -------------------------- | ---------------- | ---------------------------------------------------------------- |
| `id`                       | `string`         | UUID; the permanent identifier                                   |
| `organization_id`          | `string \| null` | Owning organization                                              |
| `project_id`               | `string`         | Owning project                                                   |
| `byte_size`                | `integer`        | Compressed size on disk                                          |
| `tags`                     | `object`         | Arbitrary key/value labels                                       |
| `ttl`                      | `integer \| null`| Seconds before automatic retirement, or `null` to disable        |
| `memory`                   | `boolean`        | Whether this snapshot includes in-memory state; always `false`   |
| `retired_at`               | `string \| null` | ISO-8601 timestamp of when the snapshot was retired, or `null` if active |
| `created_at`               | `string`         | ISO-8601 creation timestamp                                      |
| `updated_at`               | `string`         | ISO-8601 last-update timestamp                                   |

---

## Snapshot aliases

Aliases give snapshots human-readable names. An alias can be any string, like `tag` or `namespace@tag` (e.g. `my-app@v1`, `latest`, `production@2024-01`).

Aliases are mutable — you can point an alias at a different snapshot at any time, which makes them useful for rolling deploys or "latest" pointers.

```typescript
// Assign or reassign an alias
await sdk.snapshots.alias(snapshotId, "my-app@v1");

// Retrieve a snapshot by alias
const snapshot = await sdk.snapshots.getByAlias("my-app@v1");

// Retire a snapshot by id (returns the retired snapshot)
const retired = await sdk.snapshots.retire(snapshot.id);
```

When creating a sandbox, you can reference a snapshot by alias instead of UUID:

```typescript
const sandbox = await sdk.sandboxes.create({ snapshotAlias: "my-app@v1" });
```

---

## Ephemeral sandboxes

An **ephemeral** sandbox is one that takes no snapshot and is automatically deleted when it terminates. Use ephemeral sandboxes for short-lived tasks where you don't need to persist anything or restart the sandbox later. A sandbox is ephemeral when it is created **without** a `terminationPolicy`:

```typescript
// Ephemeral: no `terminationPolicy` → no snapshot, deleted on termination.
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
});
```

To keep a snapshot instead, pass `terminationPolicy` at creation:

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
  terminationPolicy: { snapshot: { aliases: ["my-app@v2"] } },
});
```

---

## Resource allocation

When creating a sandbox, you can configure its CPU and memory:

| Parameter     | Default      | Notes                        |
| ------------- | ------------ | ---------------------------- |
| `cpu`         | `1` (1 vCPU) | Cores; 0.1–16                     |
| `memoryBytes` | `2147483648` | 2 GiB                        |

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
  cpu: 2, // 2 vCPUs
  memoryBytes: 4 * 1024 ** 3, // 4 GiB
});
```

---

## Recovery

If a sandbox crashes or is lost due to infrastructure issues, the platform may attempt automatic recovery. It will ensure the files of the sandbox are persisted and a new snapshot is created.

The sandbox model exposes three fields tracking this:

| Field                  | Description                                            |
| ---------------------- | ------------------------------------------------------ |
| `recovery_status`      | `pending` → `recovered` / `canceled` / `unrecoverable` |
| `recovery_started_at`  | When recovery was initiated                            |
| `recovery_finished_at` | When recovery completed (success or failure)           |

---

## Sandbox IDs

Every sandbox has a short ID (6–8 characters, e.g. `abc123`) that you use to reference it in API calls and SDK methods. You can supply your own ID at creation time or let the platform generate one.

```typescript
const sandbox = await sdk.sandboxes.create({
  id: "my-box", // optional; auto-generated if omitted
  snapshotAlias: "my-app@v1",
});
```

---

## Connecting to a running sandbox

Once a sandbox reaches the `running` state, two fields under the sandbox model's `agent` object unlock access to the in-VM API:

| Field         | Description                                    |
| ------------- | ---------------------------------------------- |
| `agent.url`   | Base URL for the in-VM HTTP/WebSocket API      |
| `agent.token` | Bearer token required to authenticate requests |

The SDK wraps these automatically — you don't need to use them directly. The `Sandbox` object returned by `sdk.sandboxes.create()` provides high-level methods for files, directories, shell commands (execs), and ports.

---

## Quick reference: key operations

| Operation                    | TypeScript                                     | Python                                                           |
| ---------------------------- | ---------------------------------------------- | ---------------------------------------------------------------- |
| Create sandbox               | `sdk.sandboxes.create({ snapshotAlias: "…" })` | `sdk.sandboxes.create(snapshot_alias="…")`                       |
| Terminate sandbox            | `sandbox.terminate()`                          | `sandbox.terminate()`                                            |
| Terminate, alias the snapshot | `sandbox.terminate({ snapshot: { aliases: ["my-app@v2"] } })` | `sandbox.terminate(snapshot={"aliases": ["my-app@v2"]})` |
| List sandboxes               | `sdk.sandboxes.list()`                         | `sdk.sandboxes.list()`                                           |
| Create snapshot (Dockerfile) | `sdk.snapshots.create({ context: "…" })`       | `sdk.snapshots.create(CreateContextSnapshotParams(context="…"))` |
| Create snapshot (image)      | `sdk.snapshots.create({ image: "…" })`         | `sdk.snapshots.create(CreateImageSnapshotParams(image="…"))`     |
| Assign alias                 | `sdk.snapshots.alias(id, "my-app@v1")`         | `sdk.snapshots.alias(id, "my-app@v1")`                           |
| Get snapshot by alias        | `sdk.snapshots.getByAlias("my-app@v1")`        | `sdk.snapshots.get_by_alias("my-app@v1")`                        |
| List snapshots               | `sdk.snapshots.list()`                         | `sdk.snapshots.list()`                                           |
| Retire snapshot              | `sdk.snapshots.retire(id)`                     | `sdk.snapshots.retire_by_id(id)`                                 |

> **Note:** `sandboxes.list()` and `snapshots.list()` are cursor-paginated. They
> return a `Page` you can iterate directly (`for await … of` / `async for …`) to
> walk every item across pages, or step through manually with `getNextPage()` /
> `get_next_page()`. See the [TypeScript](./typescript-sdk.md) and
> [Python](./python-sdk.md) SDK references for details.

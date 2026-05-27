# Sandboxes & Snapshots

This document explains the core concepts behind Together Sandbox: what sandboxes and snapshots are, how their lifecycles work, and how they relate to each other.

---

## What is a sandbox?

A sandbox is a virtual machine that runs on Together's infrastructure. You can start one, run code inside it (via shell commands, file operations, and port forwarding), then stop it. By default, sandboxes persist between runs and can be hibernated to continue from where it left off. Sandboxes can optionally be created as **ephemeral**, in which case they cannot be hibernated and are automatically deleted when they stop.

Every sandbox is backed by a **snapshot**.

---

## What is a snapshot?

A snapshot is a compressed, immutable disk image stored in Together's registry. It defines the filesystem (and optionally the in-memory state) that a sandbox starts from.

Snapshots are created from Docker images — either by building from a Dockerfile or by referencing an existing image. Once registered, a snapshot can be used to start any number of sandboxes. They are also automatically generated when you stop a sandbox.

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
               ┌─────────┐
               │ created │
               └────┬────┘
                    │ start()
                    ▼
              ┌──────────┐
              │ starting │  ← transitional
              └────┬─────┘
                   │
                   ▼
              ┌─────────┐
              │ running │  ◄─── you interact with the sandbox here
              └────┬────┘
                   │ hibernate() or shutdown()
                   ▼
              ┌──────────┐
              │ stopping │  ← transitional
              └────┬─────┘
                   │
                   ▼
              ┌─────────┐
              │ stopped │
              └─────────┘
```

`starting` and `stopping` are transient states — the SDK's `start()`, `hibernate()`, and `shutdown()` methods all block until the sandbox reaches a terminal state (`running` or `stopped`).

**Note!** A `starting` sandbox can move to `stopping => stopped`. This happens when the sandbox was unable to start.

### Stop reasons

When a sandbox reaches the `stopped` state, the `stop_reason` field records why:

| Reason         | Description                                               |
| -------------- | --------------------------------------------------------- |
| `shutdown`     | Explicitly shut down (no memory preservation)             |
| `hibernated`   | Explicitly hibernated (memory preserved as a snapshot)    |
| `start_failed` | The sandbox failed to reach the `running` state           |
| `crashed`      | The VM process exited unexpectedly                        |
| `oom_killed`   | The sandbox ran out of memory                             |
| `evicted`      | Removed by the cluster scheduler (e.g. resource pressure) |

---

## Hibernation vs. shutdown

There are two ways to stop a running sandbox:

### Hibernate

```typescript
await sandbox.hibernate();
```

Hibernation suspends the VM and **preserves its full memory state** as a new snapshot. The next time the sandbox is started (`start_type: "resume"`), it resumes from exactly where it left off — running processes, open file descriptors, and all. Resume is fast because the OS does not need to boot.

Use hibernation when you want to pause a sandbox and come back to it later with its state intact.

> **Note:** Hibernation is not supported on ephemeral sandboxes as they do not preserve state when stopped. Calling `hibernate()` on an ephemeral sandbox returns an error. Use `shutdown()` instead.

### Shutdown

```typescript
await sandbox.shutdown();
```

Shutdown terminates the VM cleanly without preserving memory. The next start (`start_type: "cold_start"`) boots from the snapshot the sandbox was last based on, giving a clean slate. Cold starts are slower than resumes.

Use shutdown when you want a clean restart or when ongoing state doesn't matter.

---

## Sandbox versions

Each sandbox maintains a **version history** — a numbered sequence of snapshots that records the sandbox's state over time. Every time the sandbox is hibernated, a new version is created.

- `current_version_number` — the version the sandbox is currently at
- `next_version_number` — the version number that will be assigned on the next state change

You can retrieve a specific version and its associated snapshot:

```
GET /sandboxes/{sandbox_id}/versions/{number}
→ { id, sandbox_id, number, snapshot_id, created_at }
```

The `snapshot_id` from a version can then be used to create a new sandbox from that exact point in time — useful for branching or rollback. Or a version number can be used to start an existing sandbox on a specific version.

You can also get the current version from a sandbox:

```
GET /sandboxes/{sandbox_id}/versions/current
→ { id, sandbox_id, number, snapshot_id, created_at }
```

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

If you already have a Docker image (public or in a registry you can access), you can register it directly without a build step:

```typescript
const result = await sdk.snapshots.create({
  image: "python:3.12-slim",
  alias: "my-python@latest",
});
```

### Snapshot creation steps

The progress `step` field cycles through these stages:

| Step              | What's happening                                        |
| ----------------- | ------------------------------------------------------- |
| `prepare`         | Validating inputs, setting up build context             |
| `build`           | Building the Docker image (context-based only)          |
| `auth`            | Issuing registry credentials and authenticating         |
| `push`            | Pushing the image to Together's container registry      |
| `register`        | Registering the snapshot in the management API          |
| `memory-snapshot` | Creating a hibernation snapshot (memory snapshots only) |
| `alias`           | Assigning the alias to the snapshot                     |

### Memory snapshots

A **memory snapshot** is a special snapshot that includes the in-memory state of a running sandbox, not just its disk. When a sandbox is started from a memory snapshot, it resumes instantly without a cold boot — processes are already running.

Memory snapshots are created by:

1. Spinning up an ephemeral sandbox from your base snapshot
2. Waiting for initialization (e.g. startup scripts to finish)
3. Hibernating the sandbox to capture its memory state
4. Using the resulting hibernation snapshot as the memory snapshot

Pass `memorySnapshot: true` (TypeScript) or `memory_snapshot=True` (Python) to `snapshots.create()` to trigger this flow automatically.

**Note!** If a resume is not possible, the sandbox falls back to a cold start.

### Snapshot properties

| Field                      | Type      | Description                                             |
| -------------------------- | --------- | ------------------------------------------------------- |
| `id`                       | `string`  | UUID; the permanent identifier                          |
| `project_id`               | `string`  | Owning project                                          |
| `byte_size`                | `integer` | Compressed size on disk                                 |
| `protected`                | `boolean` | Protected snapshots cannot be deleted                   |
| `optimized`                | `boolean` | Whether the snapshot has been optimized for fast starts |
| `includes_memory_snapshot` | `boolean` | Whether this snapshot includes in-memory state          |
| `created_at`               | `string`  | ISO-8601 creation timestamp                             |
| `optimized_at`             | `string`  | ISO-8601 timestamp of last optimization, or `null`      |

---

## Snapshot aliases

Aliases give snapshots human-readable names. An alias can be any string, like `tag` or `namespace@tag` (e.g. `my-app@v1`, `latest`, `production@2024-01`).

Aliases are mutable — you can point an alias at a different snapshot at any time, which makes them useful for rolling deploys or "latest" pointers.

```typescript
// Assign or reassign an alias
await sdk.snapshots.alias(snapshotId, "my-app@v1");

// Retrieve a snapshot by alias
const snapshot = await sdk.snapshots.getByAlias("my-app@v1");

// Delete an alias (does not delete the snapshot)
await sdk.snapshots.deleteByAlias("my-app@v1");
```

When creating a sandbox, you can reference a snapshot by alias instead of UUID:

```typescript
const sandbox = await sdk.sandboxes.create({ snapshotAlias: "my-app@v1" });
```

---

## Ephemeral sandboxes

An **ephemeral** sandbox is one that is automatically deleted when it stops. Use ephemeral sandboxes for short-lived tasks where you don't need to persist anything or restart the sandbox later.

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
  ephemeral: true,
});
```

Ephemeral sandboxes have one important restriction: **they cannot be hibernated**. Calling `hibernate()` on an ephemeral sandbox returns an error. Only `shutdown()` is supported.

---

## Resource allocation

When creating a sandbox, you can configure its CPU, memory, and disk:

| Parameter     | Default         | Notes                     |
| ------------- | --------------- | ------------------------- |
| `millicpu`    | `1000` (1 vCPU) | Must be a multiple of 250 |
| `memoryBytes` | `2147483648`    | 2 GiB                     |
| `diskBytes`   | `10737418240`   | 10 GiB                    |

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
  millicpu: 2000, // 2 vCPUs
  memoryBytes: 4 * 1024 ** 3, // 4 GiB
  diskBytes: 20 * 1024 ** 3, // 20 GiB
});
```

---

## Recovery

If a sandbox crashes or is lost due to infrastructure issues, the platform may attempt automatic recovery. It will ensure the files of the sandbox are persisted and a new version and snapshot are created.

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

Once a sandbox reaches the `running` state, two fields in the sandbox model unlock access to the in-VM API:

| Field         | Description                                    |
| ------------- | ---------------------------------------------- |
| `agent_url`   | Base URL for the in-VM HTTP/WebSocket API      |
| `agent_token` | Bearer token required to authenticate requests |

The SDK wraps these automatically — you don't need to use them directly. The `Sandbox` object returned by `sdk.sandboxes.start()` provides high-level methods for files, directories, shell commands (execs), and ports.

---

## Quick reference: key operations

| Operation                    | TypeScript                                     | Python                                                           |
| ---------------------------- | ---------------------------------------------- | ---------------------------------------------------------------- |
| Create sandbox               | `sdk.sandboxes.create({ snapshotAlias: "…" })` | `sdk.sandboxes.create(snapshot_alias="…")`                       |
| Start sandbox                | `sdk.sandboxes.start(id)`                      | `sdk.sandboxes.start(id)`                                        |
| Hibernate sandbox            | `sandbox.hibernate()`                          | `sandbox.hibernate()`                                            |
| Shut down sandbox            | `sandbox.shutdown()`                           | `sandbox.shutdown()`                                             |
| Create snapshot (Dockerfile) | `sdk.snapshots.create({ context: "…" })`       | `sdk.snapshots.create(CreateContextSnapshotParams(context="…"))` |
| Create snapshot (image)      | `sdk.snapshots.create({ image: "…" })`         | `sdk.snapshots.create(CreateImageSnapshotParams(image="…"))`     |
| Assign alias                 | `sdk.snapshots.alias(id, "my-app@v1")`         | `sdk.snapshots.alias(id, "my-app@v1")`                           |
| Get snapshot by alias        | `sdk.snapshots.getByAlias("my-app@v1")`        | `sdk.snapshots.get_by_alias("my-app@v1")`                        |
| List snapshots               | `sdk.snapshots.list()`                         | `sdk.snapshots.list()`                                           |
| Delete snapshot              | `sdk.snapshots.deleteById(id)`                 | `sdk.snapshots.delete_by_id(id)`                                 |

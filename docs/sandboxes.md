# Sandboxes & Snapshots

This document explains the core concepts behind Together Sandbox: what sandboxes and snapshots are, how their lifecycles work, and how they relate to each other.

---

## What is a sandbox?

A sandbox is a virtual machine that runs on Together's infrastructure. You create one — it starts automatically — run code inside it (via shell commands, file operations, and port forwarding), then terminate it. When a sandbox terminates it snapshots its filesystem — and, optionally, its memory; to carry that state forward you create a new sandbox from the produced snapshot. Once terminated, a sandbox cannot be used again. Sandboxes can optionally be created as **ephemeral**, in which case they take no snapshot and are automatically deleted when they terminate.

Every sandbox is backed by a **snapshot**.

---

## What is a snapshot?

A snapshot is a compressed, immutable disk image stored in Together's registry. It defines the filesystem (and optionally the in-memory state) that a sandbox starts from.

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

The `status_reason` field always records why the sandbox is in its current status — including while `starting` (`cold_start_requested` / `restore_requested`) and `running` (`cold_started` / `restored`).

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
`snapshot` object `{ memory, aliases, ttl, tags }` selecting what to snapshot
first, plus which aliases and tags to apply to the produced snapshot. Omit it
to use the policy the sandbox was created with, or pass `null` to make the
teardown ephemeral (no snapshot).

`memory` picks between the two useful teardowns:

### Filesystem only — `{ memory: false }` (default)

```typescript
await sandbox.terminate({ snapshot: { aliases: ["my-app@v2"] } });
```

The VM is torn down cleanly without preserving memory. A new sandbox created from the resulting snapshot boots from disk with a clean slate — no in-memory state is carried over. Cold starts are slower than resumes.

Use this when you want a clean restart or when ongoing state doesn't matter.

### Filesystem and memory — `{ memory: true }`

```typescript
await sandbox.terminate({ snapshot: { memory: true, aliases: ["my-app@paused"] } });
```

This suspends the VM and **preserves its full memory state** as a new snapshot. To continue, you create a new sandbox from that snapshot; it resumes from exactly where it left off — running processes, open file descriptors, and all. This resume is fast because the OS does not need to boot.

Use it when you want to pause a sandbox and come back to it later with its state intact.

`status_reason` does not indicate whether a memory snapshot was captured. To
tell whether teardown preserved in-memory state, inspect the produced snapshot
(aliased `sandbox:<sandboxId>`): its `memory` field is `true` when a memory
snapshot was captured and `false` otherwise.

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

The SDK (or CLI) submits the build to Together's remote image-builder service, which builds the image and pushes it to the internal registry; the snapshot is then registered. No local Docker installation is required.

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
| `memory`                   | `boolean`        | Whether this snapshot includes in-memory state                   |
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

## Network policy

A sandbox can be given a **network policy** at creation: who may reach its ports (`ingress`), and what it may connect to (`egress`). Without one, a sandbox is unrestricted.

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
  networkPolicy: {
    ingress: [
      { from: "10.0.0.0/8", toPort: 80, access: "allow" },
      { from: "*", toPort: 8080, access: "deny" },
      { from: "*", toPort: 3000, access: "allow_with_token" },
    ],
    egress: [
      { to: "*", toPort: 443, access: "deny" },
      { to: "api.openai.com", toPort: 443, access: "allow" },
    ],
  },
});
```

| Field    | Values                                                                                     |
| -------- | ------------------------------------------------------------------------------------------ |
| `from`   | Ingress only: `*`, an IP, or a CIDR — the client's address.                                |
| `to`     | Egress only: `*`, an IP, a CIDR, a host name, or `*.domain` (names under the domain, not the domain itself). |
| `toPort` | A port, an inclusive range `"8000-9000"`, or `"*"`. Default: every port.                   |
| `access` | `allow` or `deny`; ingress also takes `allow_with_token`.                                  |

**Rules are unordered.** When several match, the **most specific** one decides: a host name beats any address, a longer CIDR beats a shorter one, a longer `*.domain` beats a shorter one, and only then does the port count — a single port beats a range, a narrower range beats a wider one, and either beats `*`. Between equally specific rules the more restrictive one wins. A connection no rule matches is **allowed**, so "deny everything except…" is a `*` deny plus the exceptions, in any order.

**Ingress** applies to requests reaching the sandbox's URL. `allow_with_token` admits a request only if it carries the API key that created the sandbox in the `X-Sandbox-Token` header; the header is removed before the request reaches the sandbox. This lets you put your own proxy, app, or worker in front of a sandbox port — do your own auth there, then add the header and forward.

**Egress** applies to every TCP connection the sandbox opens. Host rules are matched against the TLS SNI of an HTTPS connection, or the `Host` header of a plain HTTP one; other protocols are matched on their address only. A connection allowed by a host rule is dialled to that host, never to the address the sandbox chose, so a sandbox cannot use an allowed name to reach another address. A sandbox with any egress `deny` rule may send no UDP other than DNS (HTTP/3 clients fall back to TCP).

Whatever the policy, a sandbox can never reach private address ranges or the cloud metadata service.

**The sandbox's agent port is never closed.** Port `57468` serves the sandbox's agent — the API the SDKs and the CLI's `exec` drive the sandbox through — so a policy can narrow it but not block it:

- Only ingress rules that name `57468` **and** a specific IP or CIDR apply to it. A `*` port, a range such as `1-65535`, or a `*` client never does — so `{ from: "*", access: "deny" }` leaves the agent reachable.
- Those rules form an allow-list. If any of them admits clients (`allow` or `allow_with_token`), every other client is denied: `{ from: "10.0.0.0/8", toPort: 57468, access: "allow" }` on its own limits the agent to `10.0.0.0/8`.
- A `deny` naming the port and a client blocks just that client.

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

The sandbox model exposes one field tracking this:

| Field           | Type                     | Description                                        |
| --------------- | ------------------------ | -------------------------------------------------- |
| `recovery_at`   | `string \| null`         | When recovery last ran, or `null` if it never has  |

Progress is otherwise reflected in `status` and `status_reason`: a sandbox being
recovered reports `recovering`, moves back to `running` with a `restored` reason
on success, and lands on `unrecovered` if recovery could not complete.

---

## Sandbox IDs

Every sandbox has a platform-generated UUID that you use to reference it in API
calls and SDK methods. IDs cannot be chosen at creation time — read the assigned
one off the created sandbox:

```typescript
const sandbox = await sdk.sandboxes.create({
  snapshotAlias: "my-app@v1",
});

console.log(sandbox.id); // e.g. "3f1c8a9e-5b2d-4e7a-9c10-6d8f2b4a1e33"
```

To label sandboxes with names of your own, use `tags` and filter on them with
`sandboxes.list({ tags: { … } })`.

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
| Terminate, snapshot disk     | `sandbox.terminate({ snapshot: { aliases: ["my-app@v2"] } })` | `sandbox.terminate(snapshot={"aliases": ["my-app@v2"]})` |
| Terminate, snapshot disk+RAM | `sandbox.terminate({ snapshot: { memory: true } })` | `sandbox.terminate(snapshot={"memory": True})` |
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

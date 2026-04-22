# TypeScript SDK — `@together-sandbox/sdk`

## Installation

```bash
npm install @together-sandbox/sdk
```

Requires Node.js 18+.

---

## Authentication

Set your Together AI API key as an environment variable:

```bash
export TOGETHER_API_KEY=your_api_key
```

Or pass it directly when constructing the client (see below).

---

## Quick start

```typescript
import { TogetherSandbox } from "@together-sandbox/sdk";

const sdk = new TogetherSandbox({ apiKey: process.env.TOGETHER_API_KEY! });
const sandbox = await sdk.sandboxes.start("your-sandbox-id");

const content = await sandbox.files.read("/package.json");
console.log(content);

await sandbox.shutdown();
```

---

## `TogetherSandbox`

The main entry point for the SDK.

```typescript
const sdk = new TogetherSandbox(config: TogetherSandboxConfig);
```

### `TogetherSandboxConfig`

| Property  | Type     | Required | Description                                                                     |
| --------- | -------- | -------- | ------------------------------------------------------------------------------- |
| `apiKey`  | `string` | Yes      | Together AI API key. Falls back to `TOGETHER_API_KEY` env var if not set.       |
| `baseUrl` | `string` | No       | Override the management API base URL. Defaults to `https://api.codesandbox.io`. |

### `sdk.sandboxes`

Sandbox lifecycle namespace.

#### `sdk.sandboxes.create(body): Promise<SandboxModel>`

Creates a new sandbox record from a snapshot. Does not start the VM — call `sdk.sandboxes.start()` with the returned ID afterwards.

```typescript
const sandboxModel = await sdk.sandboxes.create({
  snapshot_alias: "my-app@v1",
  millicpu: 1000,
  memory_bytes: 512 * 1024 * 1024,
  disk_bytes: 10 * 1024 * 1024 * 1024,
});

const sandbox = await sdk.sandboxes.start(sandboxModel.id);
```

| Property         | Type      | Required | Description                                                                         |
| ---------------- | --------- | -------- | ----------------------------------------------------------------------------------- |
| `snapshot_id`    | `string`  | \*       | ID of the snapshot to use. One of `snapshot_id` or `snapshot_alias` is required.    |
| `snapshot_alias` | `string`  | \*       | Alias of the snapshot to use. One of `snapshot_id` or `snapshot_alias` is required. |
| `millicpu`       | `number`  | Yes      | CPU allocation in millicpu (must be > 0, multiple of 250).                          |
| `memory_bytes`   | `number`  | Yes      | Memory allocation in bytes.                                                         |
| `disk_bytes`     | `number`  | Yes      | Disk allocation in bytes.                                                           |
| `id`             | `string`  | No       | Sandbox ID (6–8 characters). Generated if not provided.                             |
| `ephemeral`      | `boolean` | No       | Mark the sandbox as ephemeral.                                                      |

#### `sdk.sandboxes.start(sandboxId, options?): Promise<Sandbox>`

Starts the VM for the given sandbox ID and returns a connected [`Sandbox`](#sandbox) instance.

```typescript
const sandbox = await sdk.sandboxes.start("your-sandbox-id");

// With optional start options:
const sandbox = await sdk.sandboxes.start("your-sandbox-id", {
  startOptions: { version_number: 3 },
});
```

#### `sdk.sandboxes.hibernate(sandboxId): Promise<void>`

Suspends (hibernates) a VM by sandbox ID.

```typescript
await sdk.sandboxes.hibernate("your-sandbox-id");
```

#### `sdk.sandboxes.shutdown(sandboxId): Promise<void>`

Shuts down a VM by sandbox ID.

```typescript
await sdk.sandboxes.shutdown("your-sandbox-id");
```

---

### `sdk.snapshots`

Snapshot creation namespace. Snapshots are images you can pass to `sdk.sandboxes.start()`.

#### `sdk.snapshots.create(params): Promise<CreateSnapshotResult>`

Create a snapshot from either a local Dockerfile or an existing Docker image. Requires Docker to be installed and running when building from a local context.

**From a local Dockerfile:**

```typescript
const result = await sdk.snapshots.create({
  context: "./my-app",
  dockerfile: "./my-app/Dockerfile.prod", // optional
  alias: "my-app@v1", // optional
  onProgress: (event) => console.log(event.output),
});

// Use the snapshot ID to create a sandbox:
const sandboxModel = await sdk.sandboxes.create({
  snapshot_id: result.snapshotId,
  millicpu: 1000,
  memory_bytes: 512 * 1024 * 1024,
  disk_bytes: 10 * 1024 * 1024 * 1024,
});
```

**From a public Docker image:**

```typescript
const result = await sdk.snapshots.create({
  image: "node:22",
  alias: "my-node@latest", // optional
});

// Use the alias to create a sandbox:
const sandboxModel = await sdk.sandboxes.create({
  snapshot_alias: result.alias,
  millicpu: 1000,
  memory_bytes: 512 * 1024 * 1024,
  disk_bytes: 10 * 1024 * 1024 * 1024,
});
```

##### Context variant

| Parameter    | Type                                | Description                                                                                                 |
| ------------ | ----------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `context`    | `string`                            | Path to the Docker build context directory. Mutually exclusive with `image`.                                |
| `dockerfile` | `string`                            | Path to a Dockerfile. Defaults to `Dockerfile` inside `context`. Only valid with `context`.                 |
| `alias`      | `string`                            | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the context directory name. |
| `onProgress` | `(event: SnapshotProgress) => void` | Optional progress callback. Receives `{ step, output }` at each stage.                                      |

##### Image variant

| Parameter    | Type                                | Description                                                                                                             |
| ------------ | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `image`      | `string`                            | Docker image name or reference (e.g. `node:22`, `registry.example.com/org/app:tag`). Mutually exclusive with `context`. |
| `alias`      | `string`                            | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the image name.                         |
| `onProgress` | `(event: SnapshotProgress) => void` | Optional progress callback.                                                                                             |

#### `CreateSnapshotResult`

| Property     | Type                  | Description                                           |
| ------------ | --------------------- | ----------------------------------------------------- |
| `snapshotId` | `string`              | ID of the created snapshot.                           |
| `alias`      | `string \| undefined` | The full alias (`namespace@tag`) if one was assigned. |

#### `SnapshotProgress`

| Property | Type     | Description                                                                                                 |
| -------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| `step`   | `string` | Current stage: `"prepare"`, `"build"`, `"auth"`, `"push"`, `"register"`, `"memory-snapshot"`, or `"alias"`. |
| `output` | `string` | Human-readable progress message.                                                                            |

---

## `Sandbox`

A connected, running VM. Returned by `sdk.sandboxes.start()`. All sub-namespaces are available as properties.

### Properties

| Property | Type           | Description                                |
| -------- | -------------- | ------------------------------------------ |
| `id`     | `string`       | The sandbox/VM ID.                         |
| `vmInfo` | `SandboxModel` | Raw VM start response (id, cluster, etc.). |

---

### `sandbox.files`

File system operations.

#### `files.read(path): Promise<string>`

Read the content of a file.

```typescript
const content = await sandbox.files.read("/src/index.ts");
```

#### `files.create(path, content): Promise<string>`

Create or overwrite a file. Content can be a `string`, `Blob`, or `File`.

```typescript
await sandbox.files.create("/hello.txt", "Hello, world!");
```

#### `files.delete(path): Promise<void>`

Delete a file.

```typescript
await sandbox.files.delete("/old-file.txt");
```

#### `files.move(from, to): Promise<void>`

Move a file.

```typescript
await sandbox.files.move("/src/old.ts", "/src/new.ts");
```

#### `files.copy(from, to): Promise<void>`

Copy a file.

```typescript
await sandbox.files.copy("/src/template.ts", "/src/copy.ts");
```

#### `files.stat(path): Promise<FileInfo>`

Get file metadata (size, type, modified time, etc.).

```typescript
const info = await sandbox.files.stat("/package.json");
```

#### `files.watch(path, options?): Promise<ReadableStream>`

Watch a directory for file system changes via SSE.

```typescript
const stream = await sandbox.files.watch("/src", {
  recursive: true,
  ignorePatterns: ["node_modules/**"],
});
```

`WatchOptions`:

| Property         | Type       | Description                        |
| ---------------- | ---------- | ---------------------------------- |
| `recursive`      | `boolean`  | Watch subdirectories recursively.  |
| `ignorePatterns` | `string[]` | Glob patterns for paths to ignore. |

---

### `sandbox.directories`

Directory operations.

#### `directories.list(path): Promise<FileInfo[]>`

List the contents of a directory.

```typescript
const files = await sandbox.directories.list("/src");
```

#### `directories.create(path): Promise<void>`

Create a directory (including any missing parent directories).

```typescript
await sandbox.directories.create("/src/utils");
```

#### `directories.delete(path): Promise<void>`

Delete a directory.

```typescript
await sandbox.directories.delete("/tmp/scratch");
```

---

### `sandbox.execs`

Shell execution operations.

#### `execs.list(): Promise<Exec[]>`

List all active execs.

```typescript
const execs = await sandbox.execs.list();
```

#### `execs.create(body): Promise<Exec>`

Create a new exec (run a command).

```typescript
const exec = await sandbox.execs.create({
  command: "npm",
  args: ["install"],
  cwd: "/workspace",
});
```

#### `execs.get(id): Promise<Exec>`

Get an exec by ID.

```typescript
const exec = await sandbox.execs.get("exec-id");
```

#### `execs.update(id, body): Promise<Exec>`

Update exec status.

```typescript
await sandbox.execs.update("exec-id", { status: "stopped" });
```

#### `execs.delete(id): Promise<void>`

Delete an exec.

```typescript
await sandbox.execs.delete("exec-id");
```

#### `execs.streamOutput(id, lastSequence?): Promise<ReadableStream>`

Stream exec output via SSE. Optionally provide `lastSequence` to resume from a specific point.

```typescript
const stream = await sandbox.execs.streamOutput("exec-id");
```

#### `execs.getOutput(id, lastSequence?): Promise<ExecOutput>`

One-shot poll for exec output (non-streaming).

```typescript
const output = await sandbox.execs.getOutput("exec-id");
```

#### `execs.sendStdin(id, body): Promise<void>`

Send stdin input to a running exec.

```typescript
await sandbox.execs.sendStdin("exec-id", { input: "yes\n" });
```

#### `execs.streamList(): Promise<ReadableStream>`

Stream the live list of all active execs via SSE.

```typescript
const stream = await sandbox.execs.streamList();
```

---

### `sandbox.ports`

Port discovery.

#### `ports.list(): Promise<PortInfo[]>`

List all open ports in the sandbox.

```typescript
const ports = await sandbox.ports.list();
```

#### `ports.streamList(): Promise<ReadableStream>`

Stream port changes via SSE.

```typescript
const stream = await sandbox.ports.streamList();
```

---

### Lifecycle methods

#### `sandbox.hibernate(): Promise<void>`

Suspend (hibernate) this VM.

```typescript
await sandbox.hibernate();
```

#### `sandbox.shutdown(): Promise<void>`

Shut down this VM.

```typescript
await sandbox.shutdown();
```

---

## Static factory methods on `Sandbox`

These are convenience classmethods that create a temporary SDK client internally — useful when you only need to perform a single operation.

### `Sandbox.start(sandboxId, config, options?): Promise<Sandbox>`

```typescript
const sandbox = await Sandbox.start("your-sandbox-id", {
  apiKey: process.env.TOGETHER_API_KEY!,
});
```

### `Sandbox.hibernate(sandboxId, config): Promise<void>`

```typescript
await Sandbox.hibernate("your-sandbox-id", {
  apiKey: process.env.TOGETHER_API_KEY!,
});
```

### `Sandbox.shutdown(sandboxId, config): Promise<void>`

```typescript
await Sandbox.shutdown("your-sandbox-id", {
  apiKey: process.env.TOGETHER_API_KEY!,
});
```

---

## Environment variables

| Variable           | Description                         |
| ------------------ | ----------------------------------- |
| `TOGETHER_API_KEY` | Required. Your Together AI API key. |

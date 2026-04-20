# Python SDK — `together-sandbox`

## Installation

```bash
pip install together-sandbox
```

Requires Python 3.10+.

---

## Authentication

Set your Together AI API key as an environment variable:

```bash
export TOGETHER_API_KEY=your_api_key
```

Or pass it directly when constructing the client (see below).

---

## Quick start

```python
import asyncio
from together_sandbox import TogetherSandbox

async def main():
    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env
    async with await sdk.sandboxes.start("your-sandbox-id") as sandbox:
        content = await sandbox.files.read("/package.json")
        print(content)
        await sandbox.shutdown()

asyncio.run(main())
```

> **Note:** The `async with` block closes the HTTP connection on exit. It does **not** automatically shut down the VM — call `await sandbox.shutdown()` explicitly when you're done.

---

## `TogetherSandbox`

The main entry point for the SDK.

```python
sdk = TogetherSandbox(api_key=None, base_url="https://api.codesandbox.io")
```

| Parameter  | Type          | Description                                                        |
| ---------- | ------------- | ------------------------------------------------------------------ |
| `api_key`  | `str \| None` | Together AI API key. Falls back to the `TOGETHER_API_KEY` env var. |
| `base_url` | `str`         | Management API base URL. Defaults to `https://api.codesandbox.io`. |

`TogetherSandbox` supports use as an async context manager:

```python
async with TogetherSandbox() as sdk:
    sandbox = await sdk.sandboxes.start("your-sandbox-id")
    ...
# Closes the management API HTTP connection on exit.
```

### `sdk.sandboxes`

Sandbox lifecycle namespace.

#### `sdk.sandboxes.create(body: CreateSandboxBody): Coroutine[SandboxModel]`

Creates a new sandbox record from a snapshot. Does not start the VM — call `sdk.sandboxes.start()` with the returned ID afterwards.

```python
from together_sandbox.api.models.create_sandbox_body import CreateSandboxBody

sandbox_model = await sdk.sandboxes.create(CreateSandboxBody(
    snapshot_alias="my-app@v1",
    millicpu=1000,
    memory_bytes=512 * 1024 * 1024,
    disk_bytes=10 * 1024 * 1024 * 1024,
))

sandbox = await sdk.sandboxes.start(sandbox_model.id)
```

| Parameter        | Type           | Required | Description                                                                        |
| ---------------- | -------------- | -------- | ---------------------------------------------------------------------------------- |
| `snapshot_id`    | `UUID \| Unset` | *       | ID of the snapshot to use. One of `snapshot_id` or `snapshot_alias` is required.  |
| `snapshot_alias` | `str \| Unset` | *        | Alias of the snapshot to use. One of `snapshot_id` or `snapshot_alias` is required. |
| `millicpu`       | `int`          | Yes      | CPU allocation in millicpu (must be > 0, multiple of 250).                         |
| `memory_bytes`   | `int`          | Yes      | Memory allocation in bytes.                                                        |
| `disk_bytes`     | `int`          | Yes      | Disk allocation in bytes.                                                          |
| `id`             | `str \| Unset` | No       | Sandbox ID (6–8 characters). Generated if not provided.                            |
| `ephemeral`      | `bool \| Unset` | No      | Mark the sandbox as ephemeral.                                                     |

#### `sdk.sandboxes.start(sandbox_id, *, start_options=None): Coroutine[Sandbox]`

Starts the VM for the given sandbox ID and returns a connected [`Sandbox`](#sandbox) instance.

```python
sandbox = await sdk.sandboxes.start("your-sandbox-id")

# With optional start options:
sandbox = await sdk.sandboxes.start("your-sandbox-id", start_options={"version_number": 3})
```

#### `sdk.sandboxes.hibernate(sandbox_id): Coroutine[None]`

Suspends (hibernates) a VM by sandbox ID.

```python
await sdk.sandboxes.hibernate("your-sandbox-id")
```

#### `sdk.sandboxes.shutdown(sandbox_id): Coroutine[None]`

Shuts down a VM by sandbox ID.

```python
await sdk.sandboxes.shutdown("your-sandbox-id")
```

---

### `sdk.snapshots`

Snapshot creation namespace. Snapshots are images you can pass to `sdk.sandboxes.start()`.

#### `sdk.snapshots.from_build(docker_context, params=None): Coroutine[CreateSnapshotResult]`

Build a Docker image from a local directory and register it as a snapshot. Requires Docker to be installed and running.

```python
from together_sandbox.api.models.create_sandbox_body import CreateSandboxBody

result = await sdk.snapshots.from_build("./my-app")

# Use the snapshot ID to create a sandbox:
sandbox_model = await sdk.sandboxes.create(CreateSandboxBody(
    snapshot_id=result.snapshot_id,
    millicpu=1000,
    memory_bytes=512 * 1024 * 1024,
    disk_bytes=10 * 1024 * 1024 * 1024,
))

# With a custom Dockerfile and alias:
from together_sandbox import BuildSnapshotParams

result = await sdk.snapshots.from_build("./my-app", BuildSnapshotParams(
    dockerfile="./my-app/Dockerfile.prod",
    alias="my-app@v1",
    on_progress=lambda event: print(event.output),
))
# Use the alias to create a sandbox:
sandbox_model = await sdk.sandboxes.create(CreateSandboxBody(
    snapshot_alias=result.alias,
    millicpu=1000,
    memory_bytes=512 * 1024 * 1024,
    disk_bytes=10 * 1024 * 1024 * 1024,
))
```

| Parameter              | Type                                      | Description                                                                                                 |
| ---------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `docker_context`       | `str`                                     | Path to the Docker build context directory.                                                                 |
| `params.dockerfile`    | `str \| None`                             | Path to a Dockerfile. Defaults to `Dockerfile` inside `docker_context`.                                     |
| `params.alias`         | `str \| None`                             | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the context directory name. |
| `params.on_progress`   | `Callable[[SnapshotProgress], None] \| None` | Optional progress callback. Receives a `SnapshotProgress` at each stage.                                 |

#### `sdk.snapshots.from_image(image, params=None): Coroutine[CreateSnapshotResult]`

Register an existing public Docker image as a snapshot — no local build required.

```python
result = await sdk.snapshots.from_image("node:22")
print(result.snapshot_id)

# With an alias:
from together_sandbox import CreateSnapshotParams

result = await sdk.snapshots.from_image("python:3.12-slim", CreateSnapshotParams(
    alias="my-python@latest",
))
```

| Parameter            | Type                                         | Description                                                                                     |
| -------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `image`              | `str`                                        | Docker image name or reference (e.g. `node:22`, `registry.example.com/org/app:tag`).           |
| `params.alias`       | `str \| None`                                | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the image name. |
| `params.on_progress` | `Callable[[SnapshotProgress], None] \| None` | Optional progress callback.                                                                     |

#### `CreateSnapshotResult`

| Property      | Type          | Description                                               |
| ------------- | ------------- | --------------------------------------------------------- |
| `snapshot_id` | `str`         | ID of the created snapshot.                               |
| `alias`       | `str \| None` | The full alias (`namespace@tag`) if one was assigned.     |

#### `SnapshotProgress`

| Property | Type  | Description                                                                                                                      |
| -------- | ----- | -------------------------------------------------------------------------------------------------------------------------------- |
| `step`   | `str` | Current stage: `"prepare"`, `"build"`, `"auth"`, `"push"`, `"register"`, `"memory-snapshot"`, or `"alias"`. |
| `output` | `str` | Human-readable progress message.                                                                                                 |

---

## `Sandbox`

A connected, running VM. Returned by `sdk.sandboxes.start()`. All sub-namespaces are available as properties.

```python
async with await sdk.sandboxes.start("sandbox-id") as sandbox:
    ...
```

### Properties

| Property  | Type           | Description                                 |
| --------- | -------------- | ------------------------------------------- |
| `id`      | `str`          | The sandbox/VM ID.                          |
| `vm_info` | `SandboxModel` | Raw VM start response (id, agent_url, etc.) |

---

### `sandbox.files`

File system operations.

#### `files.read(path) -> str`

Read the content of a file.

```python
content = await sandbox.files.read("/src/main.py")
```

#### `files.create(path, content) -> str`

Create or overwrite a file. Content can be `str` (encoded as UTF-8) or `bytes`.

```python
await sandbox.files.create("/hello.txt", "Hello, world!")
await sandbox.files.create("/data.bin", b"\x00\x01\x02")
```

#### `files.delete(path) -> None`

Delete a file.

```python
await sandbox.files.delete("/old-file.txt")
```

#### `files.move(from_path, to_path) -> None`

Move a file.

```python
await sandbox.files.move("/src/old.py", "/src/new.py")
```

#### `files.copy(from_path, to_path) -> None`

Copy a file.

```python
await sandbox.files.copy("/src/template.py", "/src/copy.py")
```

#### `files.stat(path) -> FileInfo`

Get file metadata (size, type, modified time, etc.).

```python
info = await sandbox.files.stat("/package.json")
```

#### `files.watch(path, *, recursive=None, ignore_patterns=None) -> AsyncIterator[dict]`

Watch a directory for file system changes via SSE. Returns an async iterator of event dicts.

```python
async for event in sandbox.files.watch("/src", recursive=True, ignore_patterns=["node_modules"]):
    print(event)
```

| Parameter         | Type                | Description                        |
| ----------------- | ------------------- | ---------------------------------- |
| `recursive`       | `bool \| None`      | Watch subdirectories recursively.  |
| `ignore_patterns` | `list[str] \| None` | Glob patterns for paths to ignore. |

---

### `sandbox.directories`

Directory operations.

#### `directories.list(path) -> list[FileInfo]`

List the contents of a directory.

```python
files = await sandbox.directories.list("/src")
```

#### `directories.create(path) -> None`

Create a directory.

```python
await sandbox.directories.create("/src/utils")
```

#### `directories.delete(path) -> None`

Delete a directory.

```python
await sandbox.directories.delete("/tmp/scratch")
```

---

### `sandbox.execs`

Shell execution operations.

#### `execs.list() -> list[Exec]`

List all active execs.

```python
execs = await sandbox.execs.list()
```

#### `execs.create(body: CreateExecRequest) -> Exec`

Create a new exec (run a command).

```python
from together_sandbox.sandbox.models.create_exec_request import CreateExecRequest

exec_ = await sandbox.execs.create(CreateExecRequest(
    command="npm",
    args=["install"],
    cwd="/workspace",
))
```

#### `execs.get(id_) -> Exec`

Get an exec by ID.

```python
exec_ = await sandbox.execs.get("exec-id")
```

#### `execs.update(id_, body: UpdateExecRequest) -> Exec`

Update exec status.

```python
from together_sandbox.sandbox.models.update_exec_request import UpdateExecRequest

await sandbox.execs.update("exec-id", UpdateExecRequest(status="stopped"))
```

#### `execs.delete(id_) -> None`

Delete an exec.

```python
await sandbox.execs.delete("exec-id")
```

#### `execs.stream_output(id_, last_sequence=None) -> AsyncIterator[dict]`

Stream exec output via SSE. Optionally provide `last_sequence` to resume from a specific point.

```python
async for chunk in sandbox.execs.stream_output("exec-id"):
    print(chunk)
```

#### `execs.get_output(id_, last_sequence=None) -> str`

One-shot poll for exec output (non-streaming).

```python
output = await sandbox.execs.get_output("exec-id")
```

#### `execs.send_stdin(id_, body: ExecStdin) -> None`

Send stdin input to a running exec.

```python
from together_sandbox.sandbox.models.exec_stdin import ExecStdin

await sandbox.execs.send_stdin("exec-id", ExecStdin(input="yes\n"))
```

#### `execs.stream_list() -> AsyncIterator[dict]`

Stream the live list of all active execs via SSE.

```python
async for update in sandbox.execs.stream_list():
    print(update)
```

---

### `sandbox.tasks`

Task operations.

#### `tasks.list() -> list[Task]`

List all tasks.

```python
tasks = await sandbox.tasks.list()
```

#### `tasks.list_setup() -> list[SetupTask]`

List setup tasks.

```python
setup = await sandbox.tasks.list_setup()
```

#### `tasks.get(id_) -> Task`

Get a task by ID.

```python
task = await sandbox.tasks.get("task-id")
```

#### `tasks.action(id_, action_type: TaskActionType) -> TaskActionResponse`

Execute an action on a task.

```python
from together_sandbox.sandbox.models.task_action_type import TaskActionType

await sandbox.tasks.action("task-id", TaskActionType.RUN)
```

---

### `sandbox.ports`

Port discovery.

#### `ports.list() -> list[PortInfo]`

List all open ports.

```python
ports = await sandbox.ports.list()
```

#### `ports.stream_list() -> AsyncIterator[dict]`

Stream port changes via SSE.

```python
async for event in sandbox.ports.stream_list():
    print(event)
```

---

### Lifecycle methods

#### `sandbox.hibernate() -> None`

Suspend (hibernate) this VM.

```python
await sandbox.hibernate()
```

#### `sandbox.shutdown() -> None`

Shut down this VM.

```python
await sandbox.shutdown()
```

#### `sandbox.close() -> None`

Close the underlying sandbox HTTP client connection without affecting the VM state.

---

### Async context manager

`Sandbox` supports use as an async context manager. Exiting the block closes the HTTP connection but does **not** shut down the VM.

```python
async with await sdk.sandboxes.start("sandbox-id") as sandbox:
    content = await sandbox.files.read("/README.md")
    await sandbox.shutdown()
```

---

## Static factory methods on `Sandbox`

Convenience classmethods that create a temporary SDK client internally.

### `Sandbox.start(sandbox_id, *, api_key=None, base_url=..., start_options=None)`

```python
sandbox = await Sandbox.start("sandbox-id", api_key="your-key")
```

### `Sandbox.hibernate(sandbox_id, *, api_key=None, base_url=...)`

```python
await Sandbox.hibernate("sandbox-id", api_key="your-key")
```

### `Sandbox.shutdown(sandbox_id, *, api_key=None, base_url=...)`

```python
await Sandbox.shutdown("sandbox-id", api_key="your-key")
```

---

## Environment variables

| Variable           | Description                         |
| ------------------ | ----------------------------------- |
| `TOGETHER_API_KEY` | Required. Your Together AI API key. |

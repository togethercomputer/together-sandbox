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

| Parameter  | Type                  | Description                                                            |
| ---------- | --------------------- | ---------------------------------------------------------------------- |
| `api_key`  | `str \| None`         | Together AI API key. Falls back to the `TOGETHER_API_KEY` env var.     |
| `base_url` | `str`                 | Management API base URL. Defaults to `https://api.codesandbox.io`.     |
| `retry`    | `RetryConfig \| None` | Retry configuration for transient failures. See [Retry](#retry) below. |

`TogetherSandbox` supports use as an async context manager:

```python
async with TogetherSandbox() as sdk:
    sandbox = await sdk.sandboxes.start("your-sandbox-id")
    ...
# Closes the management API HTTP connection on exit.
```

### `sdk.sandboxes`

Sandbox lifecycle namespace.

#### `sdk.sandboxes.create(*, millicpu, memory_bytes, disk_bytes, id=None, snapshot_id=None, snapshot_alias=None, ephemeral=None) -> SandboxModel`

Creates a new sandbox record from a snapshot. Does not start the VM — call `sdk.sandboxes.start()` with the returned ID afterwards.

```python
sandbox_model = await sdk.sandboxes.create(
    snapshot_alias="my-app@v1",
    millicpu=1000,
    memory_bytes=512 * 1024 * 1024,
    disk_bytes=10 * 1024 * 1024 * 1024,
)

sandbox = await sdk.sandboxes.start(sandbox_model.id)
```

| Parameter        | Type           | Required | Description                                                                         |
| ---------------- | -------------- | -------- | ----------------------------------------------------------------------------------- |
| `millicpu`       | `int`          | Yes      | CPU allocation in millicpu (must be > 0, multiple of 250).                          |
| `memory_bytes`   | `int`          | Yes      | Memory allocation in bytes.                                                         |
| `disk_bytes`     | `int`          | Yes      | Disk allocation in bytes.                                                           |
| `snapshot_id`    | `str \| None`  | \*       | ID of the snapshot to use. One of `snapshot_id` or `snapshot_alias` is required.    |
| `snapshot_alias` | `str \| None`  | \*       | Alias of the snapshot to use. One of `snapshot_id` or `snapshot_alias` is required. |
| `id`             | `str \| None`  | No       | Sandbox ID (6–8 characters). Generated if not provided.                             |
| `ephemeral`      | `bool \| None` | No       | Mark the sandbox as ephemeral.                                                      |

#### `sdk.sandboxes.start(sandbox_id, *, version_number=None) -> Sandbox`

Starts the VM for the given sandbox ID and returns a connected [`Sandbox`](#sandbox) instance.

```python
sandbox = await sdk.sandboxes.start("your-sandbox-id")

# Pin a specific VM version:
sandbox = await sdk.sandboxes.start("your-sandbox-id", version_number=3)
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

Snapshot creation namespace. Snapshots are images you can pass to `sdk.sandboxes.create()`.

#### `sdk.snapshots.create(params): Coroutine[CreateSnapshotResult]`

Create a snapshot from either a local Docker context or an existing public Docker image.

**From a local Dockerfile:**

Build a Docker image from a local directory and register it as a snapshot. Requires Docker to be installed and running.

```python
from together_sandbox import CreateContextSnapshotParams

result = await sdk.snapshots.create(CreateContextSnapshotParams(
    context="./my-app",
    dockerfile="./my-app/Dockerfile.prod",  # optional
    alias="my-app@v1",                      # optional
    on_progress=lambda e: print(e.output),
))

# Use the snapshot ID to create a sandbox:
sandbox_model = await sdk.sandboxes.create(
    snapshot_id=result.snapshot_id,
    millicpu=1000,
    memory_bytes=512 * 1024 * 1024,
    disk_bytes=10 * 1024 * 1024 * 1024,
)
```

| Parameter     | Type                                         | Description                                                                                                 |
| ------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `context`     | `str`                                        | Path to the Docker build context directory.                                                                 |
| `dockerfile`  | `str \| None`                                | Path to a Dockerfile. Defaults to `Dockerfile` inside `context`.                                            |
| `alias`       | `str \| None`                                | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the context directory name. |
| `on_progress` | `Callable[[SnapshotProgress], None] \| None` | Optional progress callback. Receives a `SnapshotProgress` at each stage.                                    |

**From a public Docker image:**

Register an existing public Docker image as a snapshot — no local build required.

```python
from together_sandbox import CreateImageSnapshotParams

result = await sdk.snapshots.create(CreateImageSnapshotParams(
    image="node:22",
    alias="my-node@latest",  # optional
))
print(result.snapshot_id)
```

| Parameter     | Type                                         | Description                                                                                     |
| ------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `image`       | `str`                                        | Docker image name or reference (e.g. `node:22`, `registry.example.com/org/app:tag`).            |
| `alias`       | `str \| None`                                | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the image name. |
| `on_progress` | `Callable[[SnapshotProgress], None] \| None` | Optional progress callback.                                                                     |

#### `CreateSnapshotResult`

| Property      | Type          | Description                                           |
| ------------- | ------------- | ----------------------------------------------------- |
| `snapshot_id` | `str`         | ID of the created snapshot.                           |
| `alias`       | `str \| None` | The full alias (`namespace@tag`) if one was assigned. |

#### `SnapshotProgress`

| Property | Type  | Description                                                                                                 |
| -------- | ----- | ----------------------------------------------------------------------------------------------------------- |
| `step`   | `str` | Current stage: `"prepare"`, `"build"`, `"auth"`, `"push"`, `"register"`, `"memory-snapshot"`, or `"alias"`. |
| `output` | `str` | Human-readable progress message.                                                                            |

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

#### `execs.create(command, args, *, autorun=None, interactive=None, pty=None, cwd=None, env=None, uid=None, gid=None) -> Exec`

Create a new exec (run a command).

```python
exec_ = await sandbox.execs.create(
    command="npm",
    args=["install"],
    cwd="/workspace",
    env={"NODE_ENV": "production"},
)
```

| Parameter     | Type                     | Required | Description                                                 |
| ------------- | ------------------------ | -------- | ----------------------------------------------------------- |
| `command`     | `str`                    | Yes      | Command to execute (e.g. `"npm"`).                          |
| `args`        | `list[str]`              | Yes      | Command line arguments (e.g. `["install"]`).                |
| `autorun`     | `bool \| None`           | No       | Whether to automatically start the exec (defaults to true). |
| `interactive` | `bool \| None`           | No       | Whether to start an interactive shell session.              |
| `pty`         | `bool \| None`           | No       | Whether to start a PTY shell session.                       |
| `cwd`         | `str \| None`            | No       | Working directory for the command.                          |
| `env`         | `dict[str, str] \| None` | No       | Environment variables to set, as a plain dict.              |
| `uid`         | `int \| None`            | No       | User ID to run the command as (defaults to 1000).           |
| `gid`         | `int \| None`            | No       | Group ID to run the command as (defaults to 1000).          |

#### `execs.get(id_) -> Exec`

Get an exec by ID.

```python
exec_ = await sandbox.execs.get("exec-id")
```

#### `execs.resume(id_) -> Exec`

Resume a stopped exec (sets its status back to `running`).

```python
await sandbox.execs.resume("exec-id")
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

#### `execs.send_stdin(id_, data: str) -> None`

Send raw stdin data to a running exec.

```python
await sandbox.execs.send_stdin("exec-id", "yes\n")
```

#### `execs.resize(id_, cols: int, rows: int) -> None`

Resize the PTY for an interactive exec.

```python
await sandbox.execs.resize("exec-id", cols=80, rows=24)
```

#### `execs.stream_list() -> AsyncIterator[dict]`

Stream the live list of all active execs via SSE.

```python
async for update in sandbox.execs.stream_list():
    print(update)
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

### `Sandbox.start(sandbox_id, *, api_key=None, base_url=..., version_number=None)`

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

## Errors

### `HttpError`

Raised by SDK operations for **every** failure. Inherits from `RuntimeError`,
so existing `except RuntimeError:` clauses keep working. HTTP-level errors
(non-success status) and transport-level failures (DNS, timeout, connection
refused) both surface as `HttpError`, distinguished by the `status` field.

| Attribute | Type    | Description                                                                           |
| --------- | ------- | ------------------------------------------------------------------------------------- |
| `args`    | `tuple` | Standard exception args — first element is the formatted message.                     |
| `status`  | `int`   | HTTP status code, or `0` as a sentinel for transport failures (no response received). |

Because `0` is not a valid HTTP status, `e.status == 0` cleanly identifies
"the request never reached the server" without losing the rest of the
error-handling shape. The original transport exception (`httpx.TimeoutException`,
`httpx.ConnectError`, `httpx.RemoteProtocolError`) is preserved on
`__cause__` for debugging tracebacks.

```python
from together_sandbox import HttpError

try:
    await sdk.sandboxes.start("...")
except HttpError as e:
    if e.status == 0:
        # transport-level failure (DNS / timeout / connection refused)
        raise
    elif e.status == 404:
        return None  # not found
    raise
```

---

## Retry

All operations automatically retry on transient failures. By default:

- **HTTP status codes** `408`, `429`, `500`, `502`, `503`, `504` trigger a retry.
- **Transport-level failures** (`httpx.TimeoutException`, `httpx.ConnectError`, `httpx.RemoteProtocolError`) — these surface as `HttpError` with `status == 0` — trigger a retry.
- **3 total attempts** (1 initial + 2 retries).
- **Exponential backoff**: starts at 0.5 s, doubles each attempt, plus up to 0.25 s of random jitter.

Pass a `RetryConfig` to `TogetherSandbox(retry=...)` to customise this behaviour.

### `RetryConfig`

`RetryConfig` is a dataclass — instantiate it with keyword arguments.

| Field          | Type                                                        | Default | Description                                                                                                                                                                                          |
| -------------- | ----------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `max_attempts` | `int`                                                       | `3`     | Total number of attempts (including the first). Set to `1` to disable retries.                                                                                                                       |
| `should_retry` | `Callable[[RetryContext], bool \| float] \| Awaitable[...]` | `None`  | Override the retry decision. Return `False` to abort immediately, `True` to retry with the default backoff delay, or a `float` (seconds) to retry after a custom delay. May be a coroutine function. |
| `on_retry`     | `Callable[[RetryContext], None] \| Awaitable[None]`         | `None`  | Called before each retry. Use for logging, metrics, or UI progress updates. May be a coroutine function.                                                                                             |

### `RetryContext`

| Field       | Type          | Description                                                                                  |
| ----------- | ------------- | -------------------------------------------------------------------------------------------- |
| `operation` | `str`         | The operation that failed, e.g. `'startSandbox'`, `'files.read'`.                            |
| `attempt`   | `int`         | 1-based number of the attempt that just failed.                                              |
| `error`     | `Exception`   | The [`HttpError`](#httperror) that was raised.                                               |
| `status`    | `int \| None` | HTTP status code, or `0` for transport-level failures.                                       |
| `delay`     | `float`       | **Seconds** to wait before the next attempt (default computed, override via `should_retry`). |

### Example

```python
import asyncio
from together_sandbox import TogetherSandbox, RetryConfig, RetryContext

async def main():
    sdk = TogetherSandbox(
        api_key="...",
        retry=RetryConfig(
            max_attempts=4,
            should_retry=lambda ctx: (
                # Never retry snapshot creation — it is not idempotent
                False if ctx.operation == "snapshots.create"
                # Give up on auth errors
                else False if ctx.status in (401, 403)
                # Retry everything else with default backoff
                else True
            ),
            on_retry=lambda ctx: print(
                f"[retry] {ctx.operation} attempt {ctx.attempt} failed "
                f"({'transport' if ctx.status == 0 else f'HTTP {ctx.status}'}) "
                f"— retrying in {ctx.delay:.2f}s"
            ),
        ),
    )

asyncio.run(main())
```

> **Note — `snapshots.create` is not idempotent.** Retrying after a transient 500 once the snapshot has already been created will register a duplicate. Exclude it via `should_retry` as shown above, or use the shorthand:
>
> ```python
> RetryConfig(should_retry=lambda ctx: ctx.operation != "snapshots.create")
> ```

---

## Environment variables

| Variable           | Description                         |
| ------------------ | ----------------------------------- |
| `TOGETHER_API_KEY` | Required. Your Together AI API key. |

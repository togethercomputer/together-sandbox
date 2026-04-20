# CLI — `@together-sandbox/cli`

The `together-sandbox` CLI lets you create snapshots from Dockerfiles or existing Docker images and publish them for use with Together Sandbox.

## Installation

```bash
npm install -g @together-sandbox/cli
```

Or use it without installing via `npx`:

```bash
npx @together-sandbox/cli snapshots from-build ./my-project
```

---

## Authentication

The CLI reads your Together AI API key from the environment:

```bash
export TOGETHER_API_KEY=your_api_key
```

This must be set before running any command. The CLI will exit with an error if the key is missing.

---

## Commands

### `together-sandbox snapshots`

Snapshot management commands.

---

### `together-sandbox snapshots from-build <dockerContext>`

Build a snapshot from a Dockerfile. The build context is the directory passed as `<dockerContext>`.

Under the hood this command:

1. Builds a Docker image from the context directory (using a Dockerfile in that directory, or one supplied via `--dockerFile`).
2. Authenticates with the Together Sandbox Docker registry.
3. Pushes the image to the registry.
4. Registers a snapshot backed by that image.
5. Optionally assigns an alias to the snapshot.

```bash
together-sandbox snapshots from-build <dockerContext> [options]
```

#### Arguments

| Argument          | Description                                           |
| ----------------- | ----------------------------------------------------- |
| `<dockerContext>` | Path to the Docker build context directory. Required. |

#### Options

| Option         | Type     | Description                                                                                                                                                      |
| -------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--dockerFile` | `string` | Path to a Dockerfile to use for the build. Defaults to `Dockerfile` inside `<dockerContext>`.                                                                    |
| `--alias`      | `string` | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the `<dockerContext>` directory name. Max 64 characters each; `a-z A-Z 0-9 - _`. |

#### Examples

Build from the current directory:

```bash
together-sandbox snapshots from-build .
```

Build with a custom Dockerfile and assign an alias:

```bash
together-sandbox snapshots from-build ./my-app --dockerFile ./my-app/Dockerfile.prod --alias my-app@v1
```

---

### `together-sandbox snapshots from-image <image>`

Create a snapshot from an existing public Docker image — no local build required.

```bash
together-sandbox snapshots from-image <image> [options]
```

#### Arguments

| Argument  | Description                               |
| --------- | ----------------------------------------- |
| `<image>` | Docker image name or reference. Required. |

#### Options

| Option    | Type     | Description                                                                                                                                |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `--alias` | `string` | Alias for the snapshot. Format: `tag` or `namespace@tag`. Namespace defaults to the image name. Max 64 characters each; `a-z A-Z 0-9 - _`. |

#### Examples

Create a snapshot from a public image:

```bash
together-sandbox snapshots from-image node:22
```

Create a snapshot with an alias:

```bash
together-sandbox snapshots from-image python:3.12-slim --alias my-python@latest
```

---

## Output

On success, both subcommands print the snapshot ID or alias:

```
✔ Snapshot created: my-app@v1
```

Use the snapshot ID or alias to create new sandboxes via the SDK:

```typescript
// TypeScript
const sandboxModel = await sdk.sandboxes.create({
  snapshot_alias: "my-app@v1",
  millicpu: 1000,
  memory_bytes: 512 * 1024 * 1024,
  disk_bytes: 10 * 1024 * 1024 * 1024,
});
const sandbox = await sdk.sandboxes.start(sandboxModel.id);
```

```python
# Python
from together_sandbox.api.models.create_sandbox_body import CreateSandboxBody

sandbox_model = await sdk.sandboxes.create(CreateSandboxBody(
    snapshot_alias="my-app@v1",
    millicpu=1000,
    memory_bytes=512 * 1024 * 1024,
    disk_bytes=10 * 1024 * 1024 * 1024,
))
sandbox = await sdk.sandboxes.start(sandbox_model.id)
```

---

## Prerequisites

- **Docker** must be installed and running for `snapshots from-build`. The CLI will report an error if Docker is unavailable. `snapshots from-image` does not require Docker.
- **`TOGETHER_API_KEY`** environment variable must be set.

---

## Environment variables

| Variable            | Description                                     |
| ------------------- | ----------------------------------------------- |
| `TOGETHER_API_KEY`  | Required. Your Together AI API key.             |
| `TOGETHER_BASE_URL` | Optional. Override the management API base URL. |

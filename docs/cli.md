# CLI — `@together-sandbox/cli`

The `together-sandbox` CLI lets you create snapshots from Dockerfiles or existing Docker images and publish them for use with Together Sandbox.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash
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

### `together-sandbox snapshots create [options]`

Create a snapshot from a Dockerfile (local build) or an existing public Docker image.

Under the hood for `--context`, this command:

1. Builds a Docker image from the context directory (using a Dockerfile in that directory, or one supplied via `--dockerfile`).
2. Authenticates with the Together Sandbox Docker registry.
3. Pushes the image to the registry.
4. Registers a snapshot backed by that image.
5. Optionally assigns an alias to the snapshot.

For `--image`, the image reference is registered directly as a snapshot without a local build.

```bash
together-sandbox snapshots create [options]
```

#### Options

| Option                | Type      | Description                                                                                                  |
| --------------------- | --------- | ------------------------------------------------------------------------------------------------------------ |
| `--context <dir>`     | `string`  | Path to the Docker build context directory. Mutually exclusive with `--image`.                               |
| `--dockerfile <file>` | `string`  | Path to a Dockerfile (only with `--context`). Defaults to `Dockerfile` inside `--context`.                   |
| `--image <ref>`       | `string`  | Docker image reference. Mutually exclusive with `--context`.                                                 |
| `--alias <alias>`     | `string`  | Alias for the snapshot (`tag` or `namespace@tag`).                                                           |
| `--ci`                | `boolean` | CI mode: plain stdout with no spinner. On success, only the snapshot ID is written to stdout. Default: off.  |

> **Note on `--context`.** Builds happen with your local Docker daemon — the CLI bundles the TypeScript SDK, which currently always builds locally. Docker must be installed and running.

#### Examples

Build from the current directory:

```bash
together-sandbox snapshots create --context .
```

Build with a custom Dockerfile and assign an alias:

```bash
together-sandbox snapshots create --context ./my-app --dockerfile ./my-app/Dockerfile.prod --alias my-app@v1
```

Create a snapshot from a public image:

```bash
together-sandbox snapshots create --image node:22
```

Create a snapshot from a public image with an alias:

```bash
together-sandbox snapshots create --image python:3.12-slim --alias my-python@latest
```

---

## Output

**Interactive mode (default):** the command prints a spinner-driven progress log, then a success line on completion:

```
✔ Snapshot created: <snapshot-id> (my-app@v1)
```

**CI mode (`--ci`):** progress events are printed as plain lines to stdout, and the final stdout line is the bare snapshot ID — easy to capture into a shell variable:

```bash
SNAPSHOT_ID=$(together-sandbox snapshots create --ci --context ./my-app)
```

Use the snapshot ID (or alias) to create sandboxes via the SDK — see the [TypeScript SDK](typescript-sdk.md) or [Python SDK](python-sdk.md) docs.

---

## Prerequisites

- **Docker** must be installed and running for `snapshots create --context`. The CLI will report an error if Docker is unavailable. `snapshots create --image` does not require Docker.
- **`TOGETHER_API_KEY`** environment variable must be set.

---

## Environment variables

| Variable            | Description                                     |
| ------------------- | ----------------------------------------------- |
| `TOGETHER_API_KEY`  | Required. Your Together AI API key.             |
| `TOGETHER_BASE_URL` | Optional. Override the management API base URL. |

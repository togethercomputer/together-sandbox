# CLI — `@together-sandbox/cli`

The `together-sandbox` CLI lets you build memory snapshots from local project directories and publish them as sandbox templates.

## Installation

```bash
npm install -g @together-sandbox/cli
```

Or use it without installing via `npx`:

```bash
npx @together-sandbox/cli build ./my-project
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

### `together-sandbox build <directory>`

Builds an efficient memory snapshot from a local project directory. The snapshot is used to spin up sandboxes quickly.

Under the hood this command:

1. Prepares a Docker build environment (creates a Dockerfile if one isn't present).
2. Builds a Docker image from the project directory.
3. Authenticates with the CodeSandbox Docker registry.
4. Pushes the image to the registry.
5. Creates a sandbox template backed by that image.
6. Starts the template sandbox, waits for it to initialise, then shuts it down to capture a memory snapshot.
7. Optionally assigns an alias to the template for easy reference.

```bash
together-sandbox build <directory> [options]
```

#### Arguments

| Argument      | Description                                            |
| ------------- | ------------------------------------------------------ |
| `<directory>` | Path to the project directory to build from. Required. |

#### Options

| Option           | Type      | Default | Description                                                                                                                                                                  |
| ---------------- | --------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--name`         | `string`  | —       | Display name for the resulting sandbox template.                                                                                                                             |
| `--alias`        | `string`  | —       | Alias that points to the created template. Format: `alias` or `namespace@alias`. Namespace defaults to the directory name. Characters: `a-z A-Z 0-9 - _`, max 64 chars each. |
| `--from-sandbox` | `string`  | —       | ID of an existing sandbox to use as the base template instead of the default.                                                                                                |
| `--vm-tier`      | `string`  | `Micro` | VM size for the template sandbox. One of: `Pico`, `Nano`, `Micro`, `Small`, `Medium`, `Large`, `XLarge`.                                                                     |
| `--ci`           | `boolean` | `false` | CI mode — exits the process with a non-zero code on any error.                                                                                                               |
| `--log-path`     | `string`  | —       | Relative path to write log output to a file.                                                                                                                                 |

#### Examples

Build from the current directory with a name:

```bash
together-sandbox build . --name "My Node App"
```

Build and assign a simple alias:

```bash
together-sandbox build ./my-app --alias my-app
```

Build and assign a namespaced alias:

```bash
together-sandbox build ./my-app --alias my-namespace@v1
```

Build from an existing sandbox as a base, using a larger VM:

```bash
together-sandbox build ./my-app --from-sandbox abc123 --vm-tier Large
```

Run in CI (non-zero exit on failure):

```bash
together-sandbox build . --ci
```

#### Output

On success the CLI prints the sandbox template ID (or alias) and a code snippet for creating a sandbox from it:

```
✔ Template created with tag: tpl_abc123

  Create sandbox from template using

  SDK:

    sdk.sandboxes.create({
      id: "tpl_abc123"
    })

  CLI:

    csb sandboxes fork tpl_abc123
```

---

## Prerequisites

- **Docker** must be installed and running. The `build` command calls Docker to build and push the image. The CLI will report an error if Docker is unavailable.
- **`TOGETHER_API_KEY`** environment variable must be set.

---

## Environment variables

| Variable            | Description                                     |
| ------------------- | ----------------------------------------------- |
| `TOGETHER_API_KEY`  | Required. Your Together AI API key.             |
| `TOGETHER_BASE_URL` | Optional. Override the management API base URL. |

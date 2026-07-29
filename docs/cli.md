# CLI — `together-sandbox-cli`

The `together-sandbox` CLI lets you create snapshots from Dockerfiles or existing Docker images, and create, inspect, and run commands in sandboxes.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | bash
```

This downloads a self-contained binary — no Node.js, no clone, no `npm install`. It installs to `~/.local/bin` (or `$XDG_BIN_HOME`), creating the directory if needed, and **never uses `sudo`**. If that directory isn't on your `PATH`, the installer prints the exact line to add for your shell.

| Variable      | Default                             | Purpose                                                                    |
| ------------- | ----------------------------------- | -------------------------------------------------------------------------- |
| `INSTALL_DIR` | `$XDG_BIN_HOME`, else `~/.local/bin` | Where to put the binary. Must be a directory you own.                      |
| `VERSION`     | `latest`                            | Pin a release. Accepts `3.2.0`, `v3.2.0`, or the full tag.                 |

```bash
# Install somewhere else
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | INSTALL_DIR=~/bin bash

# Pin a version
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | VERSION=3.2.0 bash
```

Prebuilt binaries exist for macOS (arm64, x64), Linux (arm64, x64), and Windows x64; on Windows use Git Bash.

Running as root works — useful in containers and CI. Note the installer resolves its default prefix from `$HOME`, so under `sudo` on Linux that is usually `/root/.local/bin` rather than your own home. Set `INSTALL_DIR` explicitly if you want it elsewhere:

```bash
curl -fsSL https://raw.githubusercontent.com/togethercomputer/together-sandbox/main/install.sh | INSTALL_DIR=/usr/local/bin sudo -E bash
```

> **Not on npm.** `@together-sandbox/cli` is not published, so `npx @together-sandbox/cli` will not work. Only the SDKs are published — `together-sandbox` on npm and PyPI. The CLI ships solely as the release binaries above.

---

## Quick start

Build a snapshot from a Dockerfile, then run a command inside a sandbox made
from it. This uses the Dockerfile in
[`examples/read-file-python-sdk/template`](../examples/read-file-python-sdk/template),
which is an Ubuntu image with `curl` and `git`, and a `/workspace/hello.txt`.

```bash
export TOGETHER_API_KEY="your-key-here"
```

**1. Build the snapshot.** The build runs on Together's image-builder service,
so no local Docker is needed:

```bash
together-sandbox snapshot create \
  --context examples/read-file-python-sdk/template \
  --alias quickstart@v1
```

```
✔ Snapshot created: 4490bbc0-3f3a-4866-b1ea-2aa7f1069920 (quickstart@v1)
```

**2. Run a command in it.** `sandbox run` creates a sandbox from the snapshot,
runs the command, and with `--rm` tears the sandbox down afterwards. A leading
`@` means "resolve this as an alias":

```bash
together-sandbox sandbox run @quickstart@v1 --rm -- uname -a
```

```
Linux 6.1.0 #1 SMP x86_64 GNU/Linux
```

Progress notices go to stderr, so stdout carries only the command's output —
`together-sandbox sandbox run @quickstart@v1 --rm -- uname -a 2>/dev/null`
gives you just the `uname` line.

**Or keep the sandbox and exec into it repeatedly.** `sandbox create` prints the
new sandbox's id, and `exec run` streams a command inside it:

```bash
SANDBOX_ID=$(together-sandbox sandbox create @quickstart@v1 | awk '{print $3}')

together-sandbox sandbox exec run "$SANDBOX_ID" -- uname -a
together-sandbox sandbox exec run "$SANDBOX_ID" -- cat /workspace/hello.txt
together-sandbox sandbox exec run "$SANDBOX_ID" -it -- bash   # interactive shell

together-sandbox sandbox terminate "$SANDBOX_ID"
```

Sandboxes are **not** cleaned up on their own unless you pass `--rm` or a
`--ttl`, so terminate what you start. `together-sandbox sandbox list` shows
what is still running.

---

## Resource tagging

Every sandbox and snapshot the CLI creates is tagged `client=together-sandbox-cli`, so
resources created here can be told apart from those created directly through an SDK:

```bash
together-sandbox sandboxes list --tag client=together-sandbox-cli
```

A tag you set yourself wins — `--tag client=ci` stores `client=ci`, not the CLI's value.

---

## Authentication

The CLI reads your Together AI API key from the environment:

```bash
export TOGETHER_API_KEY=your_api_key
```

This must be set before running any command. The CLI will exit with an error if the key is missing.

---

## Commands

Every command group accepts both its plural and singular name, so `sandbox` and
`sandboxes`, `snapshot` and `snapshots`, `exec` and `execs` are interchangeable.
This page uses whichever reads better in context.

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

| Option                | Type      | Description                                                                                                 |
| --------------------- | --------- | ----------------------------------------------------------------------------------------------------------- |
| `--context <dir>`     | `string`  | Path to the Docker build context directory. Mutually exclusive with `--image`.                              |
| `--dockerfile <file>` | `string`  | Path to a Dockerfile (only with `--context`). Defaults to `Dockerfile` inside `--context`.                  |
| `--image <ref>`       | `string`  | Docker image reference. Mutually exclusive with `--context`.                                                |
| `--alias <alias>`     | `string`  | Alias for the snapshot (`tag` or `namespace@tag`).                                                          |
| `--cache-key <key>`   | `string`  | Share a build layer cache across builds using the same key. Requires `--context`. See below.               |
| `--ci`                | `boolean` | CI mode: plain stdout with no spinner. On success, only the snapshot ID is written to stdout. Default: off. |

> **Build mode.** By default, `--context` submits the build to Together's remote image-builder service — no local Docker is required for the build itself. Set `TOGETHER_LOCAL_BUILD=1` to fall back to building locally with your own Docker daemon and pushing to the registry from your machine:
>
> ```bash
> TOGETHER_LOCAL_BUILD=1 together-sandbox snapshots create --context ./my-app
> ```

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

Reuse the layer cache across rebuilds of the same project:

```bash
together-sandbox snapshots create --context ./my-app --cache-key my-app
```

> **Set `--cache-key` if you rebuild often.** Every snapshot is built under a freshly generated image name, so the server's default cache key — the image name minus its tag — is unique per build and never matches a previous one. Passing a stable key of your own is what makes the remote builder reuse layers. Give a family of related images the same key to have them share a cache.

---

### `together-sandbox snapshots list [options]`

List snapshots, newest cursor-paginated page first.

| Option               | Type      | Description                                                                       |
| -------------------- | --------- | --------------------------------------------------------------------------------- |
| `--limit <n>`        | `number`  | Items per page (1–100, default 20).                                               |
| `--cursor <cursor>`  | `string`  | Resume from a cursor returned by a previous page. Implies single-page output.     |
| `--exclude-retired`  | `boolean` | Hide retired snapshots. Retired snapshots are included by default.                |
| `--tag KEY=VALUE`    | `string`  | Only show snapshots carrying this tag. Repeatable; all pairs must match.          |
| `-o, --output`       | `string`  | `table` (default) or `json`.                                                      |
| `--ci`               | `boolean` | Plain output, no interactive pager.                                               |

Columns: `ID`, `SIZE`, `MEMORY`, `RETIRED`, `AGE`, `TAGS`.

On a TTY the results are streamed into your pager (`$PAGER`, or `less`), fetching the next page only as you scroll. Passing `--limit`/`--cursor`, `--ci`, or piping the output emits a single page instead.

`TAGS` renders as a sorted, comma-separated `key=value` list (`<none>` when empty). On a TTY it is truncated with `…` to keep each row on one line; when piped or under `--ci` the full value is printed, so `awk`/`cut` see whole values. The `get` commands instead list one tag per line, since they are not constrained to a single row.

`AGE` and `RETIRED` render as a relative age — `10 secs ago`, `7 mins ago`, `10 hrs ago`, `3 days ago`, `5 mos ago`, `2 yrs ago` — showing only the largest matching unit. Note these cells contain spaces, so address them by column position rather than `awk` field number; `-o json` gives the exact ISO-8601 timestamps and is the robust option for scripts.

### `together-sandbox snapshots get <ref>`

Show details for one snapshot. `<ref>` is a snapshot id, or `@alias` to look it up by alias. Supports `-o json`.

---

### `together-sandbox sandboxes`

Sandbox management commands.

### `together-sandbox sandboxes list [options]`

List sandboxes. Columns: `ID`, `STATUS`, `REASON`, `CPU`, `AGE`, `TAGS`. Same pagination, tag/age rendering, and output behaviour as `snapshots list`, plus:

| Option              | Type      | Description                                                                                                                                     |
| ------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--status <status>` | `string`  | Only show sandboxes in this status. Repeatable. One of `starting`, `running`, `terminating`, `terminated`, `failed_to_start`, `recovering`, `unrecovered`. |
| `--tag KEY=VALUE`   | `string`  | Only show sandboxes carrying this tag. Repeatable; all pairs must match.                                                                        |
| `-a, --all`         | `boolean` | Show sandboxes in every status. Cannot be combined with `--status`.                                                                             |

> **Running only by default.** With no `--status` or `--all`, the CLI lists only `running` sandboxes — an unfiltered list is dominated by terminated ones, which are rarely what you're after. This mirrors `docker ps`. `--status` replaces the default and `--all` drops it; `--tag` narrows *within* it, so combine `--tag` with `--all` to search every status.
>
> The SDKs are unaffected: `sdk.sandboxes.list()` still returns every status, matching the API.

```bash
together-sandbox sandboxes list                           # running only
together-sandbox sandboxes list --all                     # everything
together-sandbox sandboxes list --status failed_to_start  # just failures
together-sandbox sandboxes list --tag env=prod            # running, tagged env=prod
together-sandbox sandboxes list --all --tag env=prod      # any status, tagged env=prod
```

### `together-sandbox sandboxes get <id>`

Show details for one sandbox — identity, status and reason, resources, termination policy, agent, and lifecycle timestamps. Supports `-o json`.

### `together-sandbox sandboxes create <ref> [options]`

Create a sandbox from a snapshot and wait until it is running. `<ref>` is a snapshot id, or `@alias` to resolve by alias.

| Option                     | Type      | Description                                                                                                       |
| -------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------ |
| `--cpu <cores>`            | `number`  | CPU allocation in cores (0.1–16). Default 1.                                                                      |
| `--memory-bytes <bytes>`   | `number`  | Memory allocation in bytes. Default 2 GiB.                                                                        |
| `--ttl <seconds>`          | `number`  | Seconds after creation before the sandbox is automatically terminated.                                            |
| `--tag KEY=VALUE`          | `string`  | Tag the sandbox. Repeatable.                                                                                      |
| `--snapshot-on-terminate`  | `boolean` | Snapshot the sandbox when it terminates. Without this the sandbox is **ephemeral**: no snapshot, deleted on teardown. |
| `--snapshot-alias <alias>` | `string`  | With `--snapshot-on-terminate`, alias to apply to the produced snapshot. Repeatable.                              |
| `--snapshot-ttl <seconds>` | `number`  | With `--snapshot-on-terminate`, seconds before the produced snapshot expires.                                     |

```bash
together-sandbox sandboxes create @my-app@v1 --cpu 2 --snapshot-on-terminate
```

### `together-sandbox sandboxes terminate <id> [options]`

Terminate a sandbox and wait until it is torn down. Termination is permanent — to continue from where a sandbox left off, create a new one from the snapshot it produced (aliased `sandbox:<sandbox id>`).

| Option                     | Type      | Description                                                       |
| -------------------------- | --------- | ------------------------------------------------------------------- |
| `--ephemeral`              | `boolean` | Take no snapshot at all, overriding the stored policy.            |
| `--snapshot-alias <alias>` | `string`  | Alias to apply to the produced snapshot. Repeatable.              |
| `--snapshot-ttl <seconds>` | `number`  | Seconds before the produced snapshot expires.                     |
| `--snapshot-tag KEY=VALUE` | `string`  | Tag the produced snapshot. Repeatable.                            |

With no snapshot flags, the termination policy the sandbox was created with applies. `--ephemeral` cannot be combined with the other snapshot flags.

### `together-sandbox sandbox exec`

Run and inspect commands inside a sandbox. Four subcommands: `create`, `run`, `ls`, `logs`.

All of them accept:

| Option            | Type     | Description                       |
| ----------------- | -------- | --------------------------------- |
| `--cwd <dir>`     | `string` | Working directory.                |
| `--env KEY=VALUE` | `string` | Environment variable. Repeatable. |
| `--user <user>`   | `string` | Run as `user[:group]`.            |

Use `--` to separate the command from CLI flags.

### `together-sandbox sandbox exec create <id> [command..]`

Start a command and print its **exec id**, without attaching. The process keeps running after the command exits, so this is the detached form — read its output later with `exec logs`. Only the id goes to stdout, so it captures cleanly:

```bash
EXEC_ID=$(together-sandbox sandbox exec create sb-123 -- npm run build)
together-sandbox sandbox exec logs sb-123 "$EXEC_ID" -f
```

### `together-sandbox sandbox exec run <id> [command..]`

Run a command and stream it, ssh-style. Exits with the remote command's exit code.

| Option              | Type      | Description                                                                          |
| ------------------- | --------- | ------------------------------------------------------------------------------------ |
| `-i, --interactive` | `boolean` | Keep stdin open.                                                                     |
| `-t, --tty`         | `boolean` | Allocate a pseudo-TTY. With `-i` and a TTY stdin, the session runs over a websocket. |

```bash
together-sandbox sandbox exec run sb-123 -- ls -la /app
together-sandbox sandbox exec run sb-123 -it -- bash
cat data.json | together-sandbox sandbox exec run sb-123 -i -- jq .name
```

### `together-sandbox sandboxes run <ref> [command..]`

Create a sandbox from a snapshot, run a command in it, and exit with the command's exit code — docker-run style. Accepts every option from both `sandboxes create` and `sandbox exec run`, plus `--rm` to terminate the sandbox when the command exits.

Progress notices go to stderr, so stdout carries only the command's output.

```bash
together-sandbox sandboxes run @my-app@v1 --rm -- npm test
```

### `together-sandbox sandbox exec ls <id>`

List execs running (or recently run) in a sandbox. Alias `list`. Supports `-o json`.

### `together-sandbox sandbox exec logs <id> <execId> [-f]`

Print an exec's output. `-f`/`--follow` streams it until the exec exits.

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

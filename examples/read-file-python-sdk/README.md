# read-file-python-sdk

Example of using the [Together Sandbox Python SDK](https://pypi.org/project/together-sandbox/) to build a snapshot and run a sandbox. Uses `together-sandbox >= 4.0.1` from PyPI.

## What it does

1. Looks for an existing snapshot by alias (`TOGETHER_SNAPSHOT_ALIAS`, default `test-snapshot-alias-v1`).
2. If not found, builds one remotely from `template/Dockerfile`.
3. Creates a sandbox from the snapshot (it starts automatically).
4. Reads `/workspace/hello.txt` from the running sandbox and prints it.
5. Terminates the sandbox. It was created without a termination policy, so it is
   ephemeral: no snapshot is taken and it is deleted on teardown.

## Structure

```
template/Dockerfile   # Image definition — edit this to customize the environment
start_sandbox.py      # Main script
```

## Setup

```bash
# Install dependencies
uv sync

# Required
export TOGETHER_API_KEY="your-key-here"  # Together AI or CodeSandbox API key

# Optional — override the snapshot alias (default: test-snapshot-alias-v1)
export TOGETHER_SNAPSHOT_ALIAS="my-custom-alias"
```

## Run

```bash
uv run start_sandbox.py
```

The snapshot is only built on the first run. Subsequent runs reuse the existing snapshot.

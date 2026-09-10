# concurrent-starts-python-sdk

Benchmark of concurrent sandbox starts with the
[Together Sandbox Python SDK](https://pypi.org/project/together-sandbox/).
Starts 100 sandboxes at once, reports timings, then terminates them all.

## What it does

1. Looks for an existing snapshot by alias (`TOGETHER_SNAPSHOT_ALIAS`, default
   `test-snapshot-alias-v1`). If not found, builds one remotely from
   `template/Dockerfile`.
2. Creates `SANDBOX_COUNT` (default 100) sandboxes concurrently via
   `asyncio.gather`, timing each one. `sandboxes.create()` returns once the
   sandbox is running, so each duration is a full start latency.
3. Prints the average, median, min/max and p95 per-sandbox start time, plus the
   wall-clock time for the whole batch and the resulting speedup over doing the
   starts one at a time.
4. Terminates every sandbox that started. They were created without a
   termination policy, so they are ephemeral: no snapshot is taken and they are
   deleted on teardown.

Individual failures are reported and excluded from the timing stats rather than
aborting the run.

## Structure

```
template/Dockerfile     # Image definition — shared with the read-file example
concurrent_starts.py    # Main script
```

## Setup

```bash
uv sync

# Required
export TOGETHER_API_KEY="your-key-here"

# Optional
export TOGETHER_SNAPSHOT_ALIAS="my-custom-alias"  # default: test-snapshot-alias-v1
export SANDBOX_COUNT=100                          # default: 100
```

## Run

```bash
uv run concurrent_starts.py
```

Starting 100 sandboxes consumes real quota. Lower `SANDBOX_COUNT` first if your
account has a concurrency limit below that.

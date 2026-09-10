"""Start N sandboxes concurrently, time the starts, then terminate them all.

Prints the average per-sandbox start time and the wall-clock time to start all
of them — the gap between the two is the concurrency you actually got.
"""

import asyncio
import os
import statistics
import time
from pathlib import Path

from together_sandbox import (
    CreateContextSnapshotParams,
    HttpError,
    Sandbox,
    SnapshotProgress,
    TogetherSandbox,
)

# Same alias scheme as the read-file example: reusing it across runs is what
# lets this script skip the image build after the first run.
SNAPSHOT_ALIAS = os.environ.get("TOGETHER_SNAPSHOT_ALIAS", "test-snapshot-alias-v1")

COUNT = int(os.environ.get("SANDBOX_COUNT", "100"))


def on_progress(p: SnapshotProgress) -> None:
    print(f"  [{p.step}] {p.output}")


async def ensure_snapshot(sdk: TogetherSandbox) -> str:
    try:
        # A 404 here just means the snapshot has not been built yet.
        existing = await sdk.snapshots.get_by_alias(SNAPSHOT_ALIAS)
        print(f"Reusing existing snapshot: id={existing.id} alias={SNAPSHOT_ALIAS}")
        return str(existing.id)
    except HttpError as e:
        if e.status != 404:
            raise
        context = Path(__file__).parent / "template"
        print("Snapshot not found, creating from ./template/Dockerfile ...")
        result = await sdk.snapshots.create(
            CreateContextSnapshotParams(
                context=str(context),
                alias=SNAPSHOT_ALIAS,
                on_progress=on_progress,
            )
        )
        print(f"Snapshot created: id={result.snapshot_id} alias={result.alias}")
        return result.snapshot_id


async def start_one(
    sdk: TogetherSandbox, snapshot_id: str, index: int
) -> tuple[int, float, Sandbox | None, BaseException | None]:
    """Create one sandbox, returning how long the start took."""
    started = time.perf_counter()
    try:
        # create() returns once the sandbox is running, so this duration is the
        # full start latency, not just the time to enqueue the request.
        sandbox = await sdk.sandboxes.create(snapshot_id=snapshot_id)
    except BaseException as e:  # noqa: BLE001 - report failures, don't abort the run
        return index, time.perf_counter() - started, None, e
    return index, time.perf_counter() - started, sandbox, None


def print_report(durations: list[float], wall_clock: float, failures: int) -> None:
    ok = len(durations)
    print()
    print(f"=== {ok} started, {failures} failed ===")
    if durations:
        ordered = sorted(durations)
        print(f"avg start time : {statistics.fmean(durations):.2f}s")
        print(f"median         : {statistics.median(ordered):.2f}s")
        print(f"min / max      : {ordered[0]:.2f}s / {ordered[-1]:.2f}s")
        # Index rather than interpolate so p95 is an observed start time.
        print(f"p95            : {ordered[min(ok - 1, int(0.95 * ok))]:.2f}s")
    print(f"wall clock     : {wall_clock:.2f}s to start {COUNT}")
    if durations:
        print(f"speedup        : {sum(durations) / wall_clock:.1f}x vs. sequential")


async def main() -> None:
    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from the environment

    snapshot_id = await ensure_snapshot(sdk)

    print(f"Starting {COUNT} sandboxes concurrently...")
    wall_start = time.perf_counter()
    results = await asyncio.gather(
        *(start_one(sdk, snapshot_id, i) for i in range(COUNT))
    )
    wall_clock = time.perf_counter() - wall_start

    sandboxes = [s for _, _, s, _ in results if s is not None]
    durations = [d for _, d, s, _ in results if s is not None]

    try:
        for index, _, _, error in results:
            if error is not None:
                print(f"  sandbox {index} failed: {type(error).__name__}: {error}")
        print_report(durations, wall_clock, COUNT - len(sandboxes))
    finally:
        # Terminate in a `finally` so a failure above still cleans up — a
        # sandbox runs until you stop it. These were created without a
        # termination policy, so they are ephemeral: no snapshot is kept.
        print()
        print(f"Terminating {len(sandboxes)} sandboxes...")
        teardown_start = time.perf_counter()
        outcomes = await asyncio.gather(
            *(sdk.sandboxes.terminate(s.id) for s in sandboxes),
            return_exceptions=True,
        )
        leaked = [
            (s.id, o)
            for s, o in zip(sandboxes, outcomes)
            if isinstance(o, BaseException)
        ]
        for sandbox_id, error in leaked:
            print(f"  failed to terminate {sandbox_id}: {error}")
        print(
            f"Terminated {len(sandboxes) - len(leaked)}/{len(sandboxes)} "
            f"in {time.perf_counter() - teardown_start:.2f}s"
        )
        print("Done.")


asyncio.run(main())

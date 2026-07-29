import asyncio
import os
from pathlib import Path

from together_sandbox import (
    CreateContextSnapshotParams,
    HttpError,
    SnapshotProgress,
    TogetherSandbox,
)

SNAPSHOT_ALIAS = os.environ.get("TOGETHER_SNAPSHOT_ALIAS", "test-snapshot-alias-v1")


def on_progress(p: SnapshotProgress) -> None:
    print(f"  [{p.step}] {p.output}")


async def main() -> None:
    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env

    # Reuse the existing snapshot if there is one.
    try:
        existing = await sdk.snapshots.get_by_alias(SNAPSHOT_ALIAS)
        snapshot_id = str(existing.id)
        print(f"Reusing existing snapshot: id={snapshot_id} alias={SNAPSHOT_ALIAS}")
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
        snapshot_id = result.snapshot_id
        print(f"Snapshot created: id={snapshot_id} alias={result.alias}")

    print("Creating sandbox from snapshot (it starts automatically)...")

    # `async with` closes the sandbox's HTTP client on the way out. It does not
    # terminate the VM — that stays explicit, hence the `finally` below.
    async with await sdk.sandboxes.create(snapshot_id=snapshot_id) as sandbox:
        print(f"Sandbox running: {sandbox.id}")
        try:
            content = await sandbox.files.read("/workspace/hello.txt")
            print(f"/workspace/hello.txt:\n{content}")
        finally:
            # No termination policy was set at creation, so this sandbox is
            # ephemeral: it takes no snapshot and is deleted on teardown.
            #
            # Uses the namespace method rather than `sandbox.terminate()`: in
            # 4.0.1 the latter defaults its `snapshot` argument to the in-VM
            # client's UNSET sentinel instead of the management client's, and
            # raises AttributeError before sending anything.
            print("Terminating sandbox...")
            await sdk.sandboxes.terminate(sandbox.id)
            print("Done.")


asyncio.run(main())

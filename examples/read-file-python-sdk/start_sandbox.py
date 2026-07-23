import asyncio
import os
from pathlib import Path
from together_sandbox import TogetherSandbox, CreateContextSnapshotParams, SnapshotProgress, HttpError

SNAPSHOT_ALIAS = os.environ.get("TOGETHER_SNAPSHOT_ALIAS", "test-snapshot-alias-v1")


def on_progress(p: SnapshotProgress) -> None:
    print(f"  [{p.step}] {p.output}")


async def main():
    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env

    # Reuse existing snapshot if it already exists
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
    sandbox = await sdk.sandboxes.create(snapshot_id=snapshot_id)
    print(f"Sandbox running: {sandbox.id}")

    try:
        content = await sandbox.files.read("/workspace/hello.txt")
        print(f"/workspace/hello.txt:\n{content}")
    finally:
        print("Shutting down sandbox...")
        await sdk.sandboxes.shutdown(sandbox.id)
        print("Done.")


asyncio.run(main())

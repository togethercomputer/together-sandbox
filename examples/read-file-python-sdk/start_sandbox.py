import asyncio
import os
from pathlib import Path

from together_sandbox import (
    CreateContextSnapshotParams,
    HttpError,
    SnapshotProgress,
    TogetherSandbox,
)

# A snapshot can be addressed by id or by an alias you pick. Reusing the same
# alias across runs is what lets this script skip the build after the first run.
SNAPSHOT_ALIAS = os.environ.get("TOGETHER_SNAPSHOT_ALIAS", "test-snapshot-alias-v1")


def on_progress(p: SnapshotProgress) -> None:
    """Called for each build step: prepare, build, push, register, alias."""
    print(f"  [{p.step}] {p.output}")


async def main() -> None:
    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from the environment

    try:
        # A 404 here just means the snapshot has not been built yet.
        existing = await sdk.snapshots.get_by_alias(SNAPSHOT_ALIAS)
        snapshot_id = str(existing.id)
        print(f"Reusing existing snapshot: id={snapshot_id} alias={SNAPSHOT_ALIAS}")
    except HttpError as e:
        if e.status != 404:
            raise
        # Builds template/Dockerfile into a snapshot. The build runs on
        # Together's image-builder service, so no local Docker is needed.
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

    # Returns once the sandbox is running. `async with` closes the connection
    # when the block ends — it does not stop the sandbox, so terminate it too.
    async with await sdk.sandboxes.create(snapshot_id=snapshot_id) as sandbox:
        print(f"Sandbox running: {sandbox.id}")
        try:
            # Read a file that template/Dockerfile baked into the image.
            content = await sandbox.files.read("/workspace/hello.txt")
            print(f"/workspace/hello.txt:\n{content}")
        finally:
            # Terminate in a `finally` so a failure above still cleans up — a
            # sandbox runs until you stop it. This one was created without a
            # termination policy, so it is ephemeral: no snapshot is kept.
            print("Terminating sandbox...")
            await sdk.sandboxes.terminate(sandbox.id)
            print("Done.")


asyncio.run(main())

"""
Quickstart: create a snapshot, start a sandbox, execute a command, and create a file.

Requirements:
    pip install together-sandbox

Environment variables:
    TOGETHER_API_KEY        - your Together AI API key (required)
    TOGETHER_SNAPSHOT_ID    - snapshot ID to boot from (required; can use the one
                              created by this script on a second run)
    TOGETHER_DOCKER_IMAGE   - public Docker image to build a new snapshot from
                              (optional, e.g. "python:3.12-slim")
"""

from __future__ import annotations

import asyncio
import os

from together_sandbox import TogetherSandbox
from together_sandbox._snapshots import CreateImageSnapshotParams, SnapshotProgress


async def main() -> None:
    snapshot_id = os.environ.get("TOGETHER_SNAPSHOT_ID")
    docker_image = os.environ.get("TOGETHER_DOCKER_IMAGE")

    async with TogetherSandbox() as sdk:
        # Optionally create a snapshot from a public Docker image
        if docker_image:
            print(f"Creating snapshot from image: {docker_image} ...")

            def on_progress(p: SnapshotProgress) -> None:
                print(f"  [{p.step}] {p.output.strip()}")

            result = await sdk.snapshots.create(
                CreateImageSnapshotParams(
                    image=docker_image,
                    on_progress=on_progress,
                )
            )
            snapshot_id = result.snapshot_id
            print(f"Snapshot created: {snapshot_id}")
        elif not snapshot_id:
            raise RuntimeError(
                "Set TOGETHER_SNAPSHOT_ID or TOGETHER_DOCKER_IMAGE to run this script."
            )

        # Start a sandbox from the snapshot
        print("Starting sandbox...")
        sandbox = await sdk.sandboxes.create(snapshot_id=snapshot_id)
        print(f"Sandbox started: {sandbox.id}")

        try:
            # Execute a command and wait for it to finish
            result = await sandbox.execs.exec(command="echo", args=["Hello from sandbox!"])
            print(f"Command output: {result['output'].strip()}")
            print(f"Exit code: {result['exit_code']}")

            # Create a file inside the sandbox
            await sandbox.files.create("/workspace/hello.txt", "Hello, Together Sandbox!\n")
            print("File created: /workspace/hello.txt")

            # Read it back to confirm
            content = await sandbox.files.read("/workspace/hello.txt")
            print(f"File content: {content.strip()}")

        finally:
            await sdk.sandboxes.terminate(sandbox.id)
            print("Sandbox terminated.")


if __name__ == "__main__":
    asyncio.run(main())

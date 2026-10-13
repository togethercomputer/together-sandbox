import asyncio
import os
import secrets
import time
from pathlib import Path
from urllib.parse import urlparse

from together_sandbox import (
    CreateContextSnapshotParams,
    HttpError,
    SnapshotProgress,
    TogetherSandbox,
)

# Reusing the same alias across runs is what lets this script skip the build
# after the first run. Bump it when you change template/.
SNAPSHOT_ALIAS = os.environ.get("TOGETHER_SNAPSHOT_ALIAS", "computer-use-example-v1")

# Port noVNC serves the desktop on inside the sandbox.
NOVNC_PORT = 6080

# Safety net: the sandbox is terminated automatically after this many seconds
# even if this script is killed before it can clean up.
TTL_SECONDS = int(os.environ.get("TOGETHER_SANDBOX_TTL", "3600"))


def on_progress(p: SnapshotProgress) -> None:
    """Called for each build step: prepare, build, push, register, alias."""
    print(f"  [{p.step}] {p.output}")


def port_url(agent_url: str, sandbox_id: str, port: int) -> str:
    """Public URL of a port in the sandbox.

    Every port gets its own host of the form ``<sandbox-id>-<port>.<domain>``,
    so swap the agent's port in its URL for the one we want.
    """
    parsed = urlparse(agent_url)
    _, domain = parsed.hostname.split(".", 1)
    return f"{parsed.scheme}://{sandbox_id}-{port}.{domain}"


async def get_or_build_snapshot(sdk: TogetherSandbox) -> str:
    try:
        # A 404 here just means the snapshot has not been built yet.
        existing = await sdk.snapshots.get_by_alias(SNAPSHOT_ALIAS)
        print(f"Reusing existing snapshot: id={existing.id} alias={SNAPSHOT_ALIAS}")
        return str(existing.id)
    except HttpError as e:
        if e.status != 404:
            raise

    # Builds template/Dockerfile into a snapshot on Together's image-builder
    # service, so no local Docker is needed. Takes a few minutes the first time.
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


async def wait_for_port(sandbox, exec_id: str, port: int, timeout: float = 120) -> None:
    """Wait until `port` is listening, failing fast if the desktop exec dies."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if any(p.port == port for p in await sandbox.ports.list()):
            return
        result = await sandbox.execs.get_output(exec_id)
        if result["exit_code"] is not None:
            raise RuntimeError(
                f"Desktop exited with code {result['exit_code']}:\n{result['output']}"
            )
        await asyncio.sleep(1)
    raise TimeoutError(f"Port {port} did not open within {timeout:.0f}s")


async def main() -> None:
    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from the environment
    snapshot_id = await get_or_build_snapshot(sdk)

    print("Creating sandbox from snapshot (it starts automatically)...")
    # Created without a termination policy, so it is ephemeral: nothing is
    # snapshotted and it is deleted when terminated.
    async with await sdk.sandboxes.create(
        snapshot_id=snapshot_id,
        cpu=2,
        memory_bytes=4 * 1024**3,
        ttl=TTL_SECONDS,
        # Labels the sandbox so it can be picked out in `sandboxes list`.
        tags={"example": "computer-use-python-sdk"},
    ) as sandbox:
        print(f"Sandbox running: {sandbox.id}")
        try:
            # The port URL is public, so the VNC password is what keeps
            # strangers off the desktop.
            password = secrets.token_urlsafe(12)

            # autostart runs the script in the background; websockify keeps it
            # in the foreground, so the exec lives as long as the desktop does.
            desktop = await sandbox.execs.create(
                "/usr/local/bin/start-desktop.sh",
                [],
                autostart=True,
                user="1000:1000",  # the `user` account from template/Dockerfile
                env={
                    "HOME": "/home/user",
                    "VNC_PASSWORD": password,
                    "NOVNC_PORT": str(NOVNC_PORT),
                    "DESKTOP_RESOLUTION": os.environ.get("DESKTOP_RESOLUTION", "1280x800"),
                },
            )

            print(f"Starting desktop (waiting for port {NOVNC_PORT})...")
            await wait_for_port(sandbox, desktop.id, NOVNC_PORT)

            url = port_url(sandbox.vm_info.agent.url, sandbox.id, NOVNC_PORT)
            print()
            print("Desktop is ready. Open it in your browser:")
            print(f"  {url}/vnc.html?autoconnect=1&resize=remote&password={password}")
            print()
            print(f"Or open {url} and enter the password: {password}")
            print(f"The sandbox is terminated after {TTL_SECONDS}s or when you press Ctrl+C.")

            await asyncio.Event().wait()  # block until Ctrl+C
        finally:
            # Terminate in a `finally` so Ctrl+C or a failure above still
            # cleans up — a sandbox otherwise runs until its TTL expires.
            print("\nTerminating sandbox...")
            await sdk.sandboxes.terminate(sandbox.id)
            print("Done.")

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass

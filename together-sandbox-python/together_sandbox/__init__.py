"""Together Sandbox Python SDK.

Recommended entry point::

    from together_sandbox import TogetherSandbox

    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env
    async with await sdk.sandboxes.start("sandbox-id") as sb:
        content = await sb.files.read("/package.json")

Low-level clients (advanced use)::

    from together_sandbox import ApiClient, SandboxClient
"""

from ._together_sandbox import TogetherSandbox
from ._sandboxes import SandboxesNamespace
from ._types import StartOptions, CreateSandboxParams
from ._snapshots import (
    SnapshotsNamespace,
    CreateSnapshotParams,
    CreateContextSnapshotParams,
    CreateImageSnapshotParams,
    CreateSnapshotResult,
    SnapshotProgress,
    Snapshot
)
from ._sandbox import Sandbox

__all__ = [
    "TogetherSandbox",
    "Sandbox",
    "SandboxesNamespace",
    "SnapshotsNamespace",
    "StartOptions",
    "CreateSandboxParams",
    "CreateSnapshotParams",
    "CreateContextSnapshotParams",
    "CreateImageSnapshotParams",
    "CreateSnapshotResult",
    "SnapshotProgress",
    "Snapshot"
]

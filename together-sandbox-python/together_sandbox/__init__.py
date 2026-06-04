"""Together Sandbox Python SDK.

Recommended entry point::

    from together_sandbox import TogetherSandbox

    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env
    async with await sdk.sandboxes.start("sandbox-id") as sb:
        content = await sb.files.read("/package.json")

Public facade types (for annotations) live in ``together_sandbox.types`` and
are re-exported here::

    from together_sandbox import SandboxInfo, FileInfo, ExecInfo, Snapshot

Catching errors::

    from together_sandbox import HttpError

    try:
        await sdk.sandboxes.start("sandbox-id")
    except HttpError as e:
        print(e.status, str(e))

The generated OpenAPI clients under ``together_sandbox._api`` and
``together_sandbox._sandbox_client`` are internal implementation details and
are not part of the public API. See ``EXPORTED_TYPES.md`` at the repo root.
"""

from ._together_sandbox import TogetherSandbox
from ._sandbox import Sandbox
from ._snapshots import (
    CreateSnapshotParams,
    CreateContextSnapshotParams,
    CreateImageSnapshotParams,
    CreateSnapshotResult,
    SnapshotProgress,
)
from ._utils import RetryConfig, RetryContext
from .errors import HttpError
from .types import (
    SandboxInfo,
    SandboxStatus,
    StartType,
    StopReason,
    RecoveryStatus,
    FileInfo,
    WatcherEvent,
    WatcherEventType,
    ExecInfo,
    ExecStatus,
    ExecStreamKind,
    ExecOutputEvent,
    ExecResult,
    PortInfo,
    Snapshot,
)

__all__ = [
    # Entry points / classes
    "TogetherSandbox",
    "Sandbox",
    "HttpError",
    # Configuration & retry
    "RetryConfig",
    "RetryContext",
    # Sandbox lifecycle
    "SandboxInfo",
    "SandboxStatus",
    "StartType",
    "StopReason",
    "RecoveryStatus",
    # File system
    "FileInfo",
    "WatcherEvent",
    "WatcherEventType",
    # Execs
    "ExecInfo",
    "ExecStatus",
    "ExecStreamKind",
    "ExecOutputEvent",
    "ExecResult",
    # Ports
    "PortInfo",
    # Snapshots
    "Snapshot",
    "CreateSnapshotParams",
    "CreateContextSnapshotParams",
    "CreateImageSnapshotParams",
    "CreateSnapshotResult",
    "SnapshotProgress",
]

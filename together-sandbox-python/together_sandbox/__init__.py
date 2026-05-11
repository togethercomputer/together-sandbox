"""Together Sandbox Python SDK.

Recommended entry point::

    from together_sandbox import TogetherSandbox

    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env
    async with await sdk.sandboxes.start("sandbox-id") as sb:
        content = await sb.files.read("/package.json")

Low-level clients (advanced use)::

    from together_sandbox import ApiClient, SandboxClient

Catching errors::

    from together_sandbox import HttpError

    try:
        await sdk.sandboxes.start("sandbox-id")
    except HttpError as e:
        print(e.status, str(e))
"""

from ._together_sandbox import TogetherSandbox
from ._sandboxes import SandboxesNamespace
from ._snapshots import (
    SnapshotsNamespace,
    CreateSnapshotParams,
    CreateContextSnapshotParams,
    CreateImageSnapshotParams,
    CreateSnapshotResult,
    SnapshotProgress,
    Snapshot,
)
from ._sandbox import Sandbox
from together_sandbox.sandbox.models.create_exec_request import CreateExecRequest
from together_sandbox.sandbox.models.exec_stdout_type import ExecStdoutType
from ._utils import RetryConfig, RetryContext
from .errors import HttpError

__all__ = [
    "TogetherSandbox",
    "Sandbox",
    "SandboxesNamespace",
    "SnapshotsNamespace",
    "CreateSnapshotParams",
    "CreateContextSnapshotParams",
    "CreateImageSnapshotParams",
    "CreateSnapshotResult",
    "SnapshotProgress",
    "Snapshot",
    "CreateExecRequest",
    "ExecStdoutType",
    "RetryConfig",
    "RetryContext",
    "HttpError",
]

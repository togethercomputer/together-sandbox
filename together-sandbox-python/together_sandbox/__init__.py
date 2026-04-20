"""Together Sandbox Python SDK.

Recommended entry point::

    from together_sandbox import TogetherSandbox

    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env
    async with await sdk.sandboxes.start("sandbox-id") as sb:
        content = await sb.files.read_file("/package.json")

Low-level clients (advanced use)::

    from together_sandbox import ApiClient, SandboxClient
"""

from .api.client import AuthenticatedClient as ApiClient
from .facade import (
    CreateSnapshotParams,
    CreateSnapshotResult,
    Sandbox,
    SandboxesNamespace,
    SnapshotProgress,
    SnapshotsNamespace,
    TogetherSandbox,
)
from .sandbox.client import AuthenticatedClient as SandboxClient

__all__ = [
    # High-level facade (recommended)
    "TogetherSandbox",
    "Sandbox",
    "SandboxesNamespace",
    "SnapshotsNamespace",
    "CreateSnapshotParams",
    "CreateSnapshotResult",
    "SnapshotProgress",
    # Low-level clients (advanced / direct use)
    "ApiClient",
    "SandboxClient",
]

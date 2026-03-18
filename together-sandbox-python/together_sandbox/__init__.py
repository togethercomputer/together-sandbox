"""Together Sandbox Python SDK.

Recommended entry point::

    from together_sandbox import TogetherSandbox

    sdk = TogetherSandbox()  # reads TOGETHER_API_KEY from env
    async with await sdk.sandboxes.start("sandbox-id") as sb:
        content = await sb.files.read_file("/package.json")

Low-level clients (advanced use)::

    from together_sandbox import ApiClient, SandboxClient
"""

from .api.client import APIClient as ApiClient
from .facade import Sandbox, TogetherSandbox
from .sandbox.client import APIClient as SandboxClient

__all__ = [
    # High-level facade (recommended)
    "TogetherSandbox",
    "Sandbox",
    # Low-level clients (advanced / direct use)
    "ApiClient",
    "SandboxClient",
]

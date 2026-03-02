"""Together Sandbox Python SDK.

Both clients are available from this single entry point:

    from together_sandbox import ApiClient, SandboxClient

- ``ApiClient``: authenticated client for the Together/CodeSandbox REST API
  (sandbox management: create, fork, hibernate, list, etc.)

- ``SandboxClient``: authenticated client for the Pint/Sandbox REST API
  (in-sandbox operations: files, exec, tasks, etc.)

Example::

    from together_sandbox import ApiClient, SandboxClient

    api = ApiClient(base_url="https://api.together.ai/csb/sdk",
                    headers={"Authorization": "Bearer <token>"})

    sb = SandboxClient(base_url="https://<sandbox-host>",
                       headers={"Authorization": "Bearer <pint-token>"})
"""

from .api.client import APIClient as ApiClient
from .sandbox.client import APIClient as SandboxClient

__all__ = ["ApiClient", "SandboxClient"]

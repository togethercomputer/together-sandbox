"""
Mock endpoint clients for testing.

Import mock classes to use as base classes for your test doubles.
"""

from .mock_default import MockDefaultClient
from .mock_meta import MockMetaClient
from .mock_sandbox import MockSandboxClient
from .mock_templates import MockTemplatesClient
from .mock_vm import MockVmClient

__all__ = [
    "MockDefaultClient",
    "MockMetaClient",
    "MockSandboxClient",
    "MockTemplatesClient",
    "MockVmClient",
]

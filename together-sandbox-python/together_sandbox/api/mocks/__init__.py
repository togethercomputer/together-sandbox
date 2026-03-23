"""
Mock implementations for testing.

These mocks implement the Protocol contracts without requiring
network transport or authentication. Use them as base classes
in your tests.

Example:
    from myapi.mocks import MockAPIClient, MockPetsClient

    class TestPetsClient(MockPetsClient):
        async def list_pets(self, limit: int | None = None) -> list[Pet]:
            return [Pet(id=1, name='Test Pet')]

    client = MockAPIClient(pets=TestPetsClient())
"""

from .endpoints.mock_default import MockDefaultClient
from .endpoints.mock_meta import MockMetaClient
from .endpoints.mock_sandbox import MockSandboxClient
from .endpoints.mock_templates import MockTemplatesClient
from .endpoints.mock_vm import MockVmClient
from .mock_client import MockAPIClient

__all__ = [
    "MockAPIClient",
    "MockDefaultClient",
    "MockMetaClient",
    "MockSandboxClient",
    "MockTemplatesClient",
    "MockVmClient",
]

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

from .endpoints.mock_directories import MockDirectoriesClient
from .endpoints.mock_execs import MockExecsClient
from .endpoints.mock_files import MockFilesClient
from .endpoints.mock_ports import MockPortsClient
from .endpoints.mock_streams import MockStreamsClient
from .endpoints.mock_tasks import MockTasksClient
from .mock_client import MockAPIClient

__all__ = [
    "MockAPIClient",
    "MockDirectoriesClient",
    "MockExecsClient",
    "MockFilesClient",
    "MockPortsClient",
    "MockStreamsClient",
    "MockTasksClient",
]

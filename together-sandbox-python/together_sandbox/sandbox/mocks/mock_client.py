from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import APIClientProtocol
    from ..endpoints.directories import DirectoriesClientProtocol
    from ..endpoints.execs import ExecsClientProtocol
    from ..endpoints.files import FilesClientProtocol
    from ..endpoints.ports import PortsClientProtocol
    from ..endpoints.streams import StreamsClientProtocol
    from ..endpoints.tasks import TasksClientProtocol

from .endpoints.mock_directories import MockDirectoriesClient
from .endpoints.mock_execs import MockExecsClient
from .endpoints.mock_files import MockFilesClient
from .endpoints.mock_ports import MockPortsClient
from .endpoints.mock_streams import MockStreamsClient
from .endpoints.mock_tasks import MockTasksClient


class MockAPIClient:
    """
    Mock implementation of APIClient for testing.

    Auto-creates default mock implementations for all tag-based endpoint clients.
    You can override specific tag clients by passing them to the constructor.

    Example:
        # Use all defaults
        client = MockAPIClient()

        # Override specific tag client
        class MyFilesClientMock(MockFilesClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data

        client = MockAPIClient(files=MyFilesClientMock())
    """

    def __init__(
        self,
        files: "FilesClientProtocol | None" = None,
        directories: "DirectoriesClientProtocol | None" = None,
        execs: "ExecsClientProtocol | None" = None,
        tasks: "TasksClientProtocol | None" = None,
        ports: "PortsClientProtocol | None" = None,
        streams: "StreamsClientProtocol | None" = None,
    ) -> None:
        self._files = files if files is not None else MockFilesClient()
        self._directories = (
            directories if directories is not None else MockDirectoriesClient()
        )
        self._execs = execs if execs is not None else MockExecsClient()
        self._tasks = tasks if tasks is not None else MockTasksClient()
        self._ports = ports if ports is not None else MockPortsClient()
        self._streams = streams if streams is not None else MockStreamsClient()

    @property
    def files(self) -> "FilesClientProtocol":
        return self._files

    @property
    def directories(self) -> "DirectoriesClientProtocol":
        return self._directories

    @property
    def execs(self) -> "ExecsClientProtocol":
        return self._execs

    @property
    def tasks(self) -> "TasksClientProtocol":
        return self._tasks

    @property
    def ports(self) -> "PortsClientProtocol":
        return self._ports

    @property
    def streams(self) -> "StreamsClientProtocol":
        return self._streams

    async def request(self, method: str, url: str, **kwargs: Any) -> Any:
        """
        Mock request method - raises NotImplementedError.

        This is a low-level method - consider using tag-specific methods instead.
        """
        raise NotImplementedError(
            "MockAPIClient.request() not implemented. Use tag-specific methods instead."
        )

    async def close(self) -> None:
        """Mock close method - no-op for testing."""
        pass  # No cleanup needed for mocks

    async def __aenter__(self) -> "APIClientProtocol":
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit async context manager - no-op for mocks."""
        pass  # No cleanup needed for mocks

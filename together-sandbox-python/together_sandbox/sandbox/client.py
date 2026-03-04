from typing import Any, Dict, Protocol, runtime_checkable

from together_sandbox.core.auth.plugins import ApiKeyAuth
from together_sandbox.core.config import ClientConfig
from together_sandbox.core.http_transport import HttpTransport, HttpxTransport

from .endpoints.directories import DirectoriesClient, DirectoriesClientProtocol
from .endpoints.execs import ExecsClient, ExecsClientProtocol
from .endpoints.files import FilesClient, FilesClientProtocol
from .endpoints.ports import PortsClient, PortsClientProtocol
from .endpoints.streams import StreamsClient, StreamsClientProtocol
from .endpoints.tasks import TasksClient, TasksClientProtocol
from .models.type_ import Type_

@runtime_checkable
class APIClientProtocol(Protocol):
    """Protocol defining the interface of APIClient for dependency injection."""
    
    @property
    def directories(self) -> 'DirectoriesClientProtocol':
        ...
    
    @property
    def execs(self) -> 'ExecsClientProtocol':
        ...
    
    @property
    def files(self) -> 'FilesClientProtocol':
        ...
    
    @property
    def ports(self) -> 'PortsClientProtocol':
        ...
    
    @property
    def streams(self) -> 'StreamsClientProtocol':
        ...
    
    @property
    def tasks(self) -> 'TasksClientProtocol':
        ...
    
    async def request(self, method: str, url: str, **kwargs: Any) -> Any:
        ...
    
    async def close(self) -> None:
        ...
    
    async def __aenter__(self) -> 'APIClientProtocol':
        ...
    
    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object | None) -> None:
        ...


class APIClient(APIClientProtocol):
    """
Pint API (version 1.0.0)

Pint (formerly Sandbox Agent) is a Go CLI tool that exposes REST API endpoints for file operations, shell management, and task execution, designed to enable building code editor applications similar to VSCode.

The application uses file-based authentication with admin and readonly tokens, supporting CodeSandbox-compatible task management with robust workspace isolation.

## Versioning
This API uses path-based versioning. Current versions:
- **v1**: Current stable version at `/api/v1/`
- **v2**: Future version (planned) at `/api/v2/`

Unversioned endpoints (health, metrics) are available directly at the root.


Async API client with pluggable transport, tag-specific clients, and client-level
headers.

Args:
    config (ClientConfig)    : Client configuration object.
    transport (HttpTransport | None)
                             : Custom HTTP transport (optional).
    directories (DirectoriesClient)
                             : Client for 'directories' endpoints.
    execs (ExecsClient)      : Client for 'execs' endpoints.
    files (FilesClient)      : Client for 'files' endpoints.
    ports (PortsClient)      : Client for 'ports' endpoints.
    streams (StreamsClient)  : Client for 'streams' endpoints.
    tasks (TasksClient)      : Client for 'tasks' endpoints.

    """
    def __init__(self, config: ClientConfig, transport: HttpTransport | None = None) -> None:
        self.config = config
        self.transport = transport if transport is not None else HttpxTransport(str(config.base_url), config.timeout)
        self._base_url: str = str(self.config.base_url)
        self._directories: DirectoriesClient | None = None
        self._execs: ExecsClient | None = None
        self._files: FilesClient | None = None
        self._ports: PortsClient | None = None
        self._streams: StreamsClient | None = None
        self._tasks: TasksClient | None = None
    
    @property
    def directories(self) -> DirectoriesClient:
        """Client for 'directories' endpoints."""
        if self._directories is None:
            self._directories = DirectoriesClient(self.transport, self._base_url)
        return self._directories
    
    @property
    def execs(self) -> ExecsClient:
        """Client for 'execs' endpoints."""
        if self._execs is None:
            self._execs = ExecsClient(self.transport, self._base_url)
        return self._execs
    
    @property
    def files(self) -> FilesClient:
        """Client for 'files' endpoints."""
        if self._files is None:
            self._files = FilesClient(self.transport, self._base_url)
        return self._files
    
    @property
    def ports(self) -> PortsClient:
        """Client for 'ports' endpoints."""
        if self._ports is None:
            self._ports = PortsClient(self.transport, self._base_url)
        return self._ports
    
    @property
    def streams(self) -> StreamsClient:
        """Client for 'streams' endpoints."""
        if self._streams is None:
            self._streams = StreamsClient(self.transport, self._base_url)
        return self._streams
    
    @property
    def tasks(self) -> TasksClient:
        """Client for 'tasks' endpoints."""
        if self._tasks is None:
            self._tasks = TasksClient(self.transport, self._base_url)
        return self._tasks
    
    async def request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Send an HTTP request via the transport."""
        return await self.transport.request(method, url, **kwargs)
    
    async def close(self) -> None:
        """Close the underlying transport if supported."""
        if hasattr(self.transport, 'close'):
            await self.transport.close()
        else:
            pass  # Or log a warning if close is expected but not found
    
    async def __aenter__(self) -> 'APIClient':
        """Enter the async context manager. Returns self."""
        if hasattr(self.transport, '__aenter__'):
            await self.transport.__aenter__()
        return self
    
    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object | None) -> None:
        """Exit the async context manager, ensuring transport is closed."""
        if hasattr(self.transport, '__aexit__'):
            await self.transport.__aexit__(exc_type, exc_val, exc_tb)
        else:
            await self.close()
    
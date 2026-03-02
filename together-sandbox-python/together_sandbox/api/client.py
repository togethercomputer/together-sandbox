from typing import Any, Dict, Protocol, runtime_checkable

from together_sandbox.core.auth.plugins import ApiKeyAuth
from together_sandbox.core.config import ClientConfig
from together_sandbox.core.http_transport import HttpTransport, HttpxTransport

from .endpoints.default import DefaultClient, DefaultClientProtocol
from .endpoints.meta import MetaClient, MetaClientProtocol
from .endpoints.sandbox import SandboxClient, SandboxClientProtocol
from .endpoints.templates import TemplatesClient, TemplatesClientProtocol
from .endpoints.vm import VmClient, VmClientProtocol

@runtime_checkable
class APIClientProtocol(Protocol):
    """Protocol defining the interface of APIClient for dependency injection."""
    
    @property
    def default(self) -> 'DefaultClientProtocol':
        ...
    
    @property
    def meta(self) -> 'MetaClientProtocol':
        ...
    
    @property
    def sandbox(self) -> 'SandboxClientProtocol':
        ...
    
    @property
    def templates(self) -> 'TemplatesClientProtocol':
        ...
    
    @property
    def vm(self) -> 'VmClientProtocol':
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
CodeSandbox API (version 2023-07-01)


Async API client with pluggable transport, tag-specific clients, and client-level
headers.

Args:
    config (ClientConfig)    : Client configuration object.
    transport (HttpTransport | None)
                             : Custom HTTP transport (optional).
    default (DefaultClient)  : Client for 'default' endpoints.
    meta (MetaClient)        : Client for 'meta' endpoints.
    sandbox (SandboxClient)  : Client for 'sandbox' endpoints.
    templates (TemplatesClient)
                             : Client for 'templates' endpoints.
    vm (VmClient)            : Client for 'vm' endpoints.

    """
    def __init__(self, config: ClientConfig, transport: HttpTransport | None = None) -> None:
        self.config = config
        self.transport = transport if transport is not None else HttpxTransport(str(config.base_url), config.timeout)
        self._base_url: str = str(self.config.base_url)
        self._default: DefaultClient | None = None
        self._meta: MetaClient | None = None
        self._sandbox: SandboxClient | None = None
        self._templates: TemplatesClient | None = None
        self._vm: VmClient | None = None
    
    @property
    def default(self) -> DefaultClient:
        """Client for 'default' endpoints."""
        if self._default is None:
            self._default = DefaultClient(self.transport, self._base_url)
        return self._default
    
    @property
    def meta(self) -> MetaClient:
        """Client for 'meta' endpoints."""
        if self._meta is None:
            self._meta = MetaClient(self.transport, self._base_url)
        return self._meta
    
    @property
    def sandbox(self) -> SandboxClient:
        """Client for 'sandbox' endpoints."""
        if self._sandbox is None:
            self._sandbox = SandboxClient(self.transport, self._base_url)
        return self._sandbox
    
    @property
    def templates(self) -> TemplatesClient:
        """Client for 'templates' endpoints."""
        if self._templates is None:
            self._templates = TemplatesClient(self.transport, self._base_url)
        return self._templates
    
    @property
    def vm(self) -> VmClient:
        """Client for 'vm' endpoints."""
        if self._vm is None:
            self._vm = VmClient(self.transport, self._base_url)
        return self._vm
    
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
    
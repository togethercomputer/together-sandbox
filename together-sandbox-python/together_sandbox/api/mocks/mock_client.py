from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import APIClientProtocol
    from ..endpoints.default import DefaultClientProtocol
    from ..endpoints.meta import MetaClientProtocol
    from ..endpoints.sandbox import SandboxClientProtocol
    from ..endpoints.templates import TemplatesClientProtocol
    from ..endpoints.vm import VmClientProtocol

from .endpoints.mock_default import MockDefaultClient
from .endpoints.mock_meta import MockMetaClient
from .endpoints.mock_sandbox import MockSandboxClient
from .endpoints.mock_templates import MockTemplatesClient
from .endpoints.mock_vm import MockVmClient


class MockAPIClient:
    """
    Mock implementation of APIClient for testing.

    Auto-creates default mock implementations for all tag-based endpoint clients.
    You can override specific tag clients by passing them to the constructor.

    Example:
        # Use all defaults
        client = MockAPIClient()

        # Override specific tag client
        class MyMetaClientMock(MockMetaClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data

        client = MockAPIClient(meta=MyMetaClientMock())
    """

    def __init__(
        self,
        meta: "MetaClientProtocol | None" = None,
        default: "DefaultClientProtocol | None" = None,
        sandbox: "SandboxClientProtocol | None" = None,
        templates: "TemplatesClientProtocol | None" = None,
        vm: "VmClientProtocol | None" = None,
    ) -> None:
        self._meta = meta if meta is not None else MockMetaClient()
        self._default = default if default is not None else MockDefaultClient()
        self._sandbox = sandbox if sandbox is not None else MockSandboxClient()
        self._templates = templates if templates is not None else MockTemplatesClient()
        self._vm = vm if vm is not None else MockVmClient()

    @property
    def meta(self) -> "MetaClientProtocol":
        return self._meta

    @property
    def default(self) -> "DefaultClientProtocol":
        return self._default

    @property
    def sandbox(self) -> "SandboxClientProtocol":
        return self._sandbox

    @property
    def templates(self) -> "TemplatesClientProtocol":
        return self._templates

    @property
    def vm(self) -> "VmClientProtocol":
        return self._vm

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

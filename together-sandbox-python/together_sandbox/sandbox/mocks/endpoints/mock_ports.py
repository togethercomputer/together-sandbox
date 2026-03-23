from typing import TYPE_CHECKING, Any, AsyncIterator

from ...models.ports_list_response import PortsListResponse

if TYPE_CHECKING:
    pass


class MockPortsClient:
    """
    Mock implementation of PortsClient for testing.

    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.

    Example:
        class TestPortsClient(MockPortsClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """

    async def list_ports(
        self,
    ) -> PortsListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockPortsClient.list_ports() not implemented. Override this method in your test subclass."
        )

    async def stream_ports_list(
        self,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockPortsClient.stream_ports_list() not implemented. Override this method in your test subclass."
        )
        yield  # pragma: no cover

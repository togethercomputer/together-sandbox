from typing import TYPE_CHECKING

from ...models.meta_information import MetaInformation

if TYPE_CHECKING:
    pass


class MockMetaClient:
    """
    Mock implementation of MetaClient for testing.

    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.

    Example:
        class TestMetaClient(MockMetaClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """

    async def meta_info(
        self,
    ) -> MetaInformation:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockMetaClient.meta_info() not implemented. Override this method in your test subclass."
        )

from typing import TYPE_CHECKING

from ...models.template_create_request_common import TemplateCreateRequestCommon
from ...models.template_create_response import TemplateCreateResponse

if TYPE_CHECKING:
    pass


class MockTemplatesClient:
    """
    Mock implementation of TemplatesClient for testing.

    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.

    Example:
        class TestTemplatesClient(MockTemplatesClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """

    async def templates_create(
        self,
        body: TemplateCreateRequestCommon | None = None,
    ) -> TemplateCreateResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockTemplatesClient.templates_create() not implemented. Override this method in your test subclass."
        )

from typing import TYPE_CHECKING

from ...models.directory_list_response import DirectoryListResponse
from ...models.file_operation_response import FileOperationResponse

if TYPE_CHECKING:
    pass


class MockDirectoriesClient:
    """
    Mock implementation of DirectoriesClient for testing.

    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.

    Example:
        class TestDirectoriesClient(MockDirectoriesClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """

    async def create_directory(
        self,
        path: str,
    ) -> FileOperationResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockDirectoriesClient.create_directory() not implemented. Override this method in your test subclass."
        )

    async def list_directory(
        self,
        path: str,
    ) -> DirectoryListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockDirectoriesClient.list_directory() not implemented. Override this method in your test subclass."
        )

    async def delete_directory(
        self,
        path: str,
    ) -> FileOperationResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockDirectoriesClient.delete_directory() not implemented. Override this method in your test subclass."
        )

from typing import TYPE_CHECKING, Any, AsyncIterator

from ...models.create_exec_request import CreateExecRequest
from ...models.error import Error
from ...models.exec_delete_response import ExecDeleteResponse
from ...models.exec_item import ExecItem
from ...models.exec_list_response import ExecListResponse
from ...models.exec_stdin import ExecStdin
from ...models.update_exec_request import UpdateExecRequest

if TYPE_CHECKING:
    pass


class MockExecsClient:
    """
    Mock implementation of ExecsClient for testing.

    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.

    Example:
        class TestExecsClient(MockExecsClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """

    async def create_exec(
        self,
        body: CreateExecRequest,
    ) -> ExecItem:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.create_exec() not implemented. Override this method in your test subclass."
        )

    async def list_execs(
        self,
    ) -> ExecListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.list_execs() not implemented. Override this method in your test subclass."
        )

    async def get_exec(
        self,
        id_: str,
    ) -> ExecItem:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.get_exec() not implemented. Override this method in your test subclass."
        )

    async def update_exec(
        self,
        id_: str,
        body: UpdateExecRequest,
    ) -> ExecItem:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.update_exec() not implemented. Override this method in your test subclass."
        )

    async def delete_exec(
        self,
        id_: str,
    ) -> ExecDeleteResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.delete_exec() not implemented. Override this method in your test subclass."
        )

    async def get_exec_output(
        self,
        id_: str,
        last_sequence: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.get_exec_output() not implemented. Override this method in your test subclass."
        )
        yield  # pragma: no cover

    async def exec_exec_stdin(
        self,
        id_: str,
        body: ExecStdin,
    ) -> ExecItem:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.exec_exec_stdin() not implemented. Override this method in your test subclass."
        )

    async def connect_to_exec_web_socket(
        self,
        id_: str,
    ) -> Error:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.connect_to_exec_web_socket() not implemented. Override this method in your test subclass."
        )

    async def stream_execs_list(
        self,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockExecsClient.stream_execs_list() not implemented. Override this method in your test subclass."
        )
        yield  # pragma: no cover

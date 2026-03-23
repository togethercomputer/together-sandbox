from typing import TYPE_CHECKING

from ...models.get_task_response import GetTaskResponse
from ...models.setup_task_list_response import SetupTaskListResponse
from ...models.task_action_response import TaskActionResponse
from ...models.task_action_type import TaskActionType
from ...models.task_list_response import TaskListResponse

if TYPE_CHECKING:
    pass


class MockTasksClient:
    """
    Mock implementation of TasksClient for testing.

    Provides default implementations that raise NotImplementedError.
    Override methods as needed in your tests.

    Example:
        class TestTasksClient(MockTasksClient):
            async def method_name(self, ...) -> ReturnType:
                return test_data
    """

    async def list_tasks(
        self,
    ) -> TaskListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockTasksClient.list_tasks() not implemented. Override this method in your test subclass."
        )

    async def get_task(
        self,
        id_: str,
    ) -> GetTaskResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockTasksClient.get_task() not implemented. Override this method in your test subclass."
        )

    async def execute_task_action(
        self,
        id_: str,
        action_type: TaskActionType,
    ) -> TaskActionResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockTasksClient.execute_task_action() not implemented. Override this method in your test subclass."
        )

    async def list_setup_tasks(
        self,
    ) -> SetupTaskListResponse:
        """
        Mock implementation that raises NotImplementedError.

        Override this method in your test subclass to provide
        the behavior needed for your test scenario.
        """
        raise NotImplementedError(
            "MockTasksClient.list_setup_tasks() not implemented. Override this method in your test subclass."
        )

from typing import Any, Callable, Dict, NoReturn, Optional, Protocol, cast, runtime_checkable

from ..models.get_task_response import GetTaskResponse
from ..models.setup_task_list_response import SetupTaskListResponse
from ..models.task_action_response import TaskActionResponse
from ..models.task_action_type import TaskActionType
from ..models.task_list_response import TaskListResponse
from together_sandbox.core import BadRequestError, ConflictError, InternalServerError, NotFoundError, UnauthorisedError
from together_sandbox.core.cattrs_converter import structure_from_dict
from together_sandbox.core.exceptions import HTTPError
from together_sandbox.core.http_transport import HttpTransport
from together_sandbox.core.streaming_helpers import iter_bytes
from together_sandbox.core.utils import DataclassSerializer

from ..models.get_task_response import GetTaskResponse
from ..models.setup_task_list_response import SetupTaskListResponse
from ..models.task_action_response import TaskActionResponse
from ..models.task_action_type import TaskActionType
from ..models.task_list_response import TaskListResponse

@runtime_checkable
class TasksClientProtocol(Protocol):
    """Protocol defining the interface of TasksClient for dependency injection."""
    
    async def list_tasks(
    self,
    ) -> TaskListResponse: ...
    
    async def get_task(
    self,
    id_: str,
    ) -> GetTaskResponse: ...
    
    async def execute_task_action(
    self,
    id_: str,
    action_type: TaskActionType,
    ) -> TaskActionResponse: ...
    
    async def list_setup_tasks(
    self,
    ) -> SetupTaskListResponse: ...
    


class TasksClient(TasksClientProtocol):
    """Client for tasks endpoints. Uses HttpTransport for all HTTP and header management."""
    
    def __init__(self, transport: HttpTransport, base_url: str) -> None:
        self._transport = transport
        self.base_url: str = base_url
    
    async def list_tasks(
        self,
    ) -> TaskListResponse:
        """
        List all tasks
        
        Lists all configured tasks from .codesandbox/tasks.json with their current status.
        
        Returns:
            TaskListResponse: List of tasks retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 401: Unauthorized
        """
        url = f"{self.base_url}/api/v1/tasks"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), TaskListResponse)
            case 401:
                raise UnauthorisedError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), TaskListResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def get_task(
        self,
        id_: str,
    ) -> GetTaskResponse:
        """
        Get task by ID
        
        Retrieves a specific task by its ID with current status and configuration.
        
        Args:
            id (str)                 : Task identifier
        
        Returns:
            GetTaskResponse: Task retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Task ID is required
                HTTPError: 401: Unauthorized
                HTTPError: 404: Task not found
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/api/v1/tasks/{id_}"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), GetTaskResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), GetTaskResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def execute_task_action(
        self,
        id_: str,
        action_type: TaskActionType,
    ) -> TaskActionResponse:
        """
        Execute task action
        
        Executes an action on a specific task (start, stop, or restart).
        
        Args:
            id (str)                 : Task identifier
            actionType (TaskActionType)
                                     : Type of action to execute
        
        Returns:
            TaskActionResponse: Action executed successfully
        
        Raises:
            HttpError:
                HTTPError: 400: Bad Request - Task ID is required, invalid action type, or
                           invalid command
                HTTPError: 401: Unauthorized
                HTTPError: 404: Task not found
                HTTPError: 409: Conflict - Invalid state transition (e.g., task already running
                           for start, task not running for stop)
                HTTPError: 500: Internal Server Error - Failed to execute action
        """
        id_ = DataclassSerializer.serialize(id_)
        
        url = f"{self.base_url}/api/v1/tasks/{id_}/actions"
        
        params: dict[str, Any] = {
            "actionType": DataclassSerializer.serialize(action_type),
        }
        
        response = await self._transport.request(
            "PATCH", url,
            params=params,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), TaskActionResponse)
            case 400:
                raise BadRequestError(response=response)
            case 401:
                raise UnauthorisedError(response=response)
            case 404:
                raise NotFoundError(response=response)
            case 409:
                raise ConflictError(response=response)
            case 500:
                raise InternalServerError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), TaskActionResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
    
    
    async def list_setup_tasks(
        self,
    ) -> SetupTaskListResponse:
        """
        List setup tasks
        
        Lists all setup tasks with their execution status. Setup tasks are auto-executed during
        server start.
        
        Returns:
            SetupTaskListResponse: Setup tasks retrieved successfully
        
        Raises:
            HttpError:
                HTTPError: 401: Unauthorized
        """
        url = f"{self.base_url}/api/v1/setup-tasks"
        
        response = await self._transport.request(
            "GET", url,
            params=None,
            json=None,
            data=None,
            headers=None
        )
        
        # Check response status code and handle accordingly
        match response.status_code:
            case 200:
                return structure_from_dict(response.json(), SetupTaskListResponse)
            case 401:
                raise UnauthorisedError(response=response)
            case _:  # Default response
                return structure_from_dict(response.json(), SetupTaskListResponse)
        # All paths above should return or raise - this should never execute
        raise RuntimeError('Unexpected code path')  # pragma: no cover
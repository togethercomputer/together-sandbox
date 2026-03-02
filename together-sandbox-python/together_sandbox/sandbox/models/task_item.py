from dataclasses import dataclass

from .task_config import TaskConfig
from .task_status import TaskStatus

__all__ = ["TaskItem"]

@dataclass
class TaskItem:
    """
    TaskItem dataclass
    
    Args:
        config_ (TaskConfig)     : Maps from 'config'
        end_time (str)           : Task end time in RFC3339 format (maps from 'endTime')
        exec_id (str)            : Exec identifier associated with the task (maps from
                                   'execId')
        id_ (str)                : Task identifier (maps from 'id')
        start_time (str)         : Task start time in RFC3339 format (maps from 'startTime')
        status (TaskStatus)      : 
    """
    config_: TaskConfig  # Maps from 'config'
    end_time: str  # Task end time in RFC3339 format (maps from 'endTime')
    exec_id: str  # Exec identifier associated with the task (maps from 'execId')
    id_: str  # Task identifier (maps from 'id')
    start_time: str  # Task start time in RFC3339 format (maps from 'startTime')
    status: TaskStatus
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "config": "config_",
            "endTime": "end_time",
            "execId": "exec_id",
            "id": "id_",
            "startTime": "start_time",
            "status": "status",
        }
        key_transform_with_dump = {
            "config_": "config",
            "end_time": "endTime",
            "exec_id": "execId",
            "id_": "id",
            "start_time": "startTime",
            "status": "status",
        }
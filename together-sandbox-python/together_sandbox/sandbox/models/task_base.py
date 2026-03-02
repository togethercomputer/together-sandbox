from dataclasses import dataclass

from .task_status import TaskStatus

__all__ = ["TaskBase"]

@dataclass
class TaskBase:
    """
    Base schema for a task item, containing common fields shared across different task
    types.
    
    Args:
        end_time (str)           : Task end time in RFC3339 format (maps from 'endTime')
        exec_id (str)            : Exec identifier associated with the task (maps from
                                   'execId')
        start_time (str)         : Task start time in RFC3339 format (maps from 'startTime')
        status (TaskStatus)      : 
    """
    end_time: str  # Task end time in RFC3339 format (maps from 'endTime')
    exec_id: str  # Exec identifier associated with the task (maps from 'execId')
    start_time: str  # Task start time in RFC3339 format (maps from 'startTime')
    status: TaskStatus
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "endTime": "end_time",
            "execId": "exec_id",
            "startTime": "start_time",
            "status": "status",
        }
        key_transform_with_dump = {
            "end_time": "endTime",
            "exec_id": "execId",
            "start_time": "startTime",
            "status": "status",
        }
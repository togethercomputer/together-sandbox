from dataclasses import dataclass

from .task_status import TaskStatus

__all__ = ["SetupTaskItem"]

@dataclass
class SetupTaskItem:
    """
    SetupTaskItem dataclass
    
    Args:
        command (str)            : Setup task command
        end_time (str)           : Task end time in RFC3339 format (maps from 'endTime')
        exec_id (str)            : Exec identifier associated with the task (maps from
                                   'execId')
        name (str)               : Setup task name
        start_time (str)         : Task start time in RFC3339 format (maps from 'startTime')
        status (TaskStatus)      : 
    """
    command: str  # Setup task command
    end_time: str  # Task end time in RFC3339 format (maps from 'endTime')
    exec_id: str  # Exec identifier associated with the task (maps from 'execId')
    name: str  # Setup task name
    start_time: str  # Task start time in RFC3339 format (maps from 'startTime')
    status: TaskStatus
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "command": "command",
            "endTime": "end_time",
            "execId": "exec_id",
            "name": "name",
            "startTime": "start_time",
            "status": "status",
        }
        key_transform_with_dump = {
            "command": "command",
            "end_time": "endTime",
            "exec_id": "execId",
            "name": "name",
            "start_time": "startTime",
            "status": "status",
        }
from dataclasses import dataclass

from .task_preview import TaskPreview
from .task_restart import TaskRestart

__all__ = ["TaskConfig"]

@dataclass
class TaskConfig:
    """
    TaskConfig dataclass
    
    Args:
        command (str)            : 
        name (str)               : 
        preview (TaskPreview)    : 
        restart_on (TaskRestart) : Maps from 'restartOn'
        run_at_start (bool)      : Maps from 'runAtStart'
    """
    command: str
    name: str
    preview: TaskPreview
    restart_on: TaskRestart  # Maps from 'restartOn'
    run_at_start: bool  # Maps from 'runAtStart'
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "command": "command",
            "name": "name",
            "preview": "preview",
            "restartOn": "restart_on",
            "runAtStart": "run_at_start",
        }
        key_transform_with_dump = {
            "command": "command",
            "name": "name",
            "preview": "preview",
            "restart_on": "restartOn",
            "run_at_start": "runAtStart",
        }
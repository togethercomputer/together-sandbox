from dataclasses import dataclass
from typing import List

from .setup_task_item import SetupTaskItem

__all__ = ["SetupTaskListResponse"]

@dataclass
class SetupTaskListResponse:
    """
    SetupTaskListResponse dataclass
    
    Args:
        setup_tasks (List[SetupTaskItem])
                                 : Maps from 'setupTasks'
    """
    setup_tasks: List[SetupTaskItem]  # Maps from 'setupTasks'
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "setupTasks": "setup_tasks",
        }
        key_transform_with_dump = {
            "setup_tasks": "setupTasks",
        }
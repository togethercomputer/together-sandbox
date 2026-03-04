from dataclasses import dataclass
from typing import List

from .task_item import TaskItem

__all__ = ["TaskListResponse"]

@dataclass
class TaskListResponse:
    """
    TaskListResponse dataclass
    
    Args:
        tasks (List[TaskItem])   : 
    """
    tasks: List[TaskItem]
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "tasks": "tasks",
        }
        key_transform_with_dump = {
            "tasks": "tasks",
        }
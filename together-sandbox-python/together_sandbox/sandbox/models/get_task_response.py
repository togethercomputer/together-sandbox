from dataclasses import dataclass

from .task_item import TaskItem

__all__ = ["GetTaskResponse"]

@dataclass
class GetTaskResponse:
    """
    GetTaskResponse dataclass
    
    Args:
        task (TaskItem)          : 
    """
    task: TaskItem
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "task": "task",
        }
        key_transform_with_dump = {
            "task": "task",
        }
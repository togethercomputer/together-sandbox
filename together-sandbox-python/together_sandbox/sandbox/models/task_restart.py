from dataclasses import dataclass
from typing import List

__all__ = ["TaskRestart"]

@dataclass
class TaskRestart:
    """
    TaskRestart dataclass
    
    Args:
        branch (bool)            : 
        clone (bool)             : 
        files (List[str])        : 
        resume (bool)            : 
    """
    branch: bool
    clone: bool
    files: List[str]
    resume: bool
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "branch": "branch",
            "clone": "clone",
            "files": "files",
            "resume": "resume",
        }
        key_transform_with_dump = {
            "branch": "branch",
            "clone": "clone",
            "files": "files",
            "resume": "resume",
        }
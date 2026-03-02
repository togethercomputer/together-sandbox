from dataclasses import dataclass
from typing import List

from .exec_item import ExecItem

__all__ = ["ExecListResponse"]

@dataclass
class ExecListResponse:
    """
    ExecListResponse dataclass
    
    Args:
        execs (List[ExecItem])   : List of execs
    """
    execs: List[ExecItem]  # List of execs
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "execs": "execs",
        }
        key_transform_with_dump = {
            "execs": "execs",
        }
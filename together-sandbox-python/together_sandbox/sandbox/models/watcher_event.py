from dataclasses import dataclass
from datetime import datetime
from typing import List

from .type__3 import Type3

__all__ = ["WatcherEvent"]

@dataclass
class WatcherEvent:
    """
    WatcherEvent dataclass
    
    Args:
        paths (List[str])        : File paths affected by the event
        timestamp (datetime)     : Timestamp of when the event occurred
        type_ (Type3)            : Type of file system event (maps from 'type')
    """
    paths: List[str]  # File paths affected by the event
    timestamp: datetime  # Timestamp of when the event occurred
    type_: Type3  # Type of file system event (maps from 'type')
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "paths": "paths",
            "timestamp": "timestamp",
            "type": "type_",
        }
        key_transform_with_dump = {
            "paths": "paths",
            "timestamp": "timestamp",
            "type_": "type",
        }
from __future__ import annotations

from enum import Enum, unique

__all__ = ["VmCreateSessionRequestPermission"]

@unique
class VmCreateSessionRequestPermission(str, Enum):
    """
    Permission level for the session
    
    Args:
        read (str)               : Value for READ
        write (str)              : Value for WRITE
    """
    READ = "read"
    WRITE = "write"
from enum import Enum, unique

__all__ = ["UpdateExecRequestStatus"]

@unique
class UpdateExecRequestStatus(str, Enum):
    """
    Status to set for the exec (currently only 'running' is supported)
    
    Args:
        running (str)            : Value for RUNNING
    """
    RUNNING = "running"
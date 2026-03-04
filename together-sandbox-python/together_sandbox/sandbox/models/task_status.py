from enum import Enum, unique

__all__ = ["TaskStatus"]

@unique
class TaskStatus(str, Enum):
    """
    TaskStatus Enum
    
    Args:
        RUNNING (str)            : Value for RUNNING
        FINISHED (str)           : Value for FINISHED
        ERROR (str)              : Value for ERROR
        KILLED (str)             : Value for KILLED
        RESTARTING (str)         : Value for RESTARTING
        IDLE (str)               : Value for IDLE
    """
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"
    KILLED = "KILLED"
    RESTARTING = "RESTARTING"
    IDLE = "IDLE"
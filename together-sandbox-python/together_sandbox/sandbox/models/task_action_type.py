from enum import Enum, unique

__all__ = ["TaskActionType"]

@unique
class TaskActionType(str, Enum):
    """
    Type of action to execute on a task
    
    Args:
        start (str)              : Value for START
        stop (str)               : Value for STOP
        restart (str)            : Value for RESTART
    """
    START = "start"
    STOP = "stop"
    RESTART = "restart"
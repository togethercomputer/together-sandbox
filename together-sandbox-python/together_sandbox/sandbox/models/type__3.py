from enum import Enum, unique

__all__ = ["Type3"]

@unique
class Type3(str, Enum):
    """
    Type of file system event
    
    Args:
        ADD (str)                : Value for ADD
        REMOVE (str)             : Value for REMOVE
        CHANGE (str)             : Value for CHANGE
        connected (str)          : Value for CONNECTED
        error (str)              : Value for ERROR
    """
    ADD = "ADD"
    REMOVE = "REMOVE"
    CHANGE = "CHANGE"
    CONNECTED = "connected"
    ERROR = "error"
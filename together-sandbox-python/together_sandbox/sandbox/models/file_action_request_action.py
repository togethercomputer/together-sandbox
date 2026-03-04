from enum import Enum, unique

__all__ = ["FileActionRequestAction"]

@unique
class FileActionRequestAction(str, Enum):
    """
    Type of action to perform on the file
    
    Args:
        move (str)               : Value for MOVE
        copy (str)               : Value for COPY
    """
    MOVE = "move"
    COPY = "copy"
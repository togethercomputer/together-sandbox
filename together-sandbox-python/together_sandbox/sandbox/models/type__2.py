from enum import Enum, unique

__all__ = ["Type2"]

@unique
class Type2(str, Enum):
    """
    Type of the exec input
    
    Args:
        stdin (str)              : Value for STDIN
        resize (str)             : Value for RESIZE
    """
    STDIN = "stdin"
    RESIZE = "resize"
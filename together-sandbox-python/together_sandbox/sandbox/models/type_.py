from enum import Enum, unique

__all__ = ["Type_"]

@unique
class Type_(str, Enum):
    """
    Type of the exec output
    
    Args:
        stdout (str)             : Value for STDOUT
        stderr (str)             : Value for STDERR
    """
    STDOUT = "stdout"
    STDERR = "stderr"
from dataclasses import dataclass
from datetime import datetime

from .type_ import Type_

__all__ = ["ExecStdout"]

@dataclass
class ExecStdout:
    """
    ExecStdout dataclass
    
    Args:
        output (str)             : Data associated with the exec output
        sequence (int)           : Sequence number of the output message
        type_ (Type_)            : Type of the exec output (maps from 'type')
        exit_code (int | None)   : Exit code of the process (only present when process has
                                   exited) (maps from 'exitCode')
        timestamp (datetime | None)
                                 : Timestamp of when the output was generated
    """
    output: str  # Data associated with the exec output
    sequence: int  # Sequence number of the output message
    type_: Type_  # Type of the exec output (maps from 'type')
    exit_code: int | None = None  # Exit code of the process (only present when process has exited) (maps from 'exitCode')
    timestamp: datetime | None = None  # Timestamp of when the output was generated
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "exitCode": "exit_code",
            "output": "output",
            "sequence": "sequence",
            "timestamp": "timestamp",
            "type": "type_",
        }
        key_transform_with_dump = {
            "exit_code": "exitCode",
            "output": "output",
            "sequence": "sequence",
            "timestamp": "timestamp",
            "type_": "type",
        }
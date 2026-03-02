from dataclasses import dataclass
from typing import List

__all__ = ["ExecItem"]

@dataclass
class ExecItem:
    """
    ExecItem dataclass
    
    Args:
        args (List[str])         : Command line arguments
        command (str)            : Command being executed
        exit_code (int)          : Exit code of the process (only present when process has
                                   exited) (maps from 'exitCode')
        id_ (str)                : Exec unique identifier (maps from 'id')
        interactive (bool)       : Whether the exec is interactive
        pid (int)                : Process ID of the exec
        pty (bool)               : Whether the exec is using a pty
        status (str)             : Exec status (e.g., running, stopped, finished)
    """
    args: List[str]  # Command line arguments
    command: str  # Command being executed
    exit_code: int  # Exit code of the process (only present when process has exited) (maps from 'exitCode')
    id_: str  # Exec unique identifier (maps from 'id')
    interactive: bool  # Whether the exec is interactive
    pid: int  # Process ID of the exec
    pty: bool  # Whether the exec is using a pty
    status: str  # Exec status (e.g., running, stopped, finished)
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "args": "args",
            "command": "command",
            "exitCode": "exit_code",
            "id": "id_",
            "interactive": "interactive",
            "pid": "pid",
            "pty": "pty",
            "status": "status",
        }
        key_transform_with_dump = {
            "args": "args",
            "command": "command",
            "exit_code": "exitCode",
            "id_": "id",
            "interactive": "interactive",
            "pid": "pid",
            "pty": "pty",
            "status": "status",
        }
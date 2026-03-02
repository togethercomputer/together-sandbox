from dataclasses import dataclass
from typing import List

from .create_exec_request_env import CreateExecRequestEnv

__all__ = ["CreateExecRequest"]

@dataclass
class CreateExecRequest:
    """
    CreateExecRequest dataclass
    
    Args:
        args (List[str])         : Command line arguments
        command (str)            : Command to execute in the exec
        autorun (bool | None)    : Whether to automatically start the exec (defaults to
                                   true)
        cwd (str | None)         : Working directory for the command (defaults to workspace
                                   directory if not specified)
        env (CreateExecRequestEnv | None)
                                 : Environment variables to set for the command (key-value
                                   pairs)
        interactive (bool | None): Whether to start interactive shell session or not
                                   (defaults to false)
        pty (bool | None)        : Whether to start pty shell session or not (defaults to
                                   false)
    """
    args: List[str]  # Command line arguments
    command: str  # Command to execute in the exec
    autorun: bool | None = None  # Whether to automatically start the exec (defaults to true)
    cwd: str | None = None  # Working directory for the command (defaults to workspace directory if not specified)
    env: CreateExecRequestEnv | None = None  # Environment variables to set for the command (key-value pairs)
    interactive: bool | None = None  # Whether to start interactive shell session or not (defaults to false)
    pty: bool | None = None  # Whether to start pty shell session or not (defaults to false)
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "args": "args",
            "autorun": "autorun",
            "command": "command",
            "cwd": "cwd",
            "env": "env",
            "interactive": "interactive",
            "pty": "pty",
        }
        key_transform_with_dump = {
            "args": "args",
            "autorun": "autorun",
            "command": "command",
            "cwd": "cwd",
            "env": "env",
            "interactive": "interactive",
            "pty": "pty",
        }
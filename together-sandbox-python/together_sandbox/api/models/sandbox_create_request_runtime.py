from __future__ import annotations

from enum import Enum, unique

__all__ = ["SandboxCreateRequestRuntime"]

@unique
class SandboxCreateRequestRuntime(str, Enum):
    """
    Runtime to use for the sandbox. Defaults to `"browser"`.
    
    Args:
        browser (str)            : Value for BROWSER
        vm (str)                 : Value for VM
    """
    BROWSER = "browser"
    VM = "vm"
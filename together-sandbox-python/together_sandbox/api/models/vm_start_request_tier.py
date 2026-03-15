from __future__ import annotations

from enum import Enum, unique

__all__ = ["VmStartRequestTier"]

@unique
class VmStartRequestTier(str, Enum):
    """
    Determines which specs to start the VM with. If not specified, the VM will start with
    the default specs for the workspace.  You can only specify a VM tier when starting a VM
    that is inside your workspace. Specifying a VM tier for someone else's sandbox will
    return an error.  Not all tiers will be available depending on the workspace
    subscription status, and higher tiers incur higher costs. Please see
    codesandbox.io/pricing for details on specs and costs.
    
    Args:
        Pico (str)               : Value for PICO
        Nano (str)               : Value for NANO
        Micro (str)              : Value for MICRO
        Small (str)              : Value for SMALL
        Medium (str)             : Value for MEDIUM
        Large (str)              : Value for LARGE
        XLarge (str)             : Value for XLARGE
    """
    PICO = "Pico"
    NANO = "Nano"
    MICRO = "Micro"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    XLARGE = "XLarge"
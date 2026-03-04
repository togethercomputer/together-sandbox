from enum import Enum, unique

__all__ = ["VmUpdateSpecsRequestTier"]

@unique
class VmUpdateSpecsRequestTier(str, Enum):
    """
    Determines which specs to update the VM with.  Not all tiers will be available depending
    on the workspace subscription status, and higher tiers incur higher costs. Please see
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
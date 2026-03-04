from dataclasses import dataclass

from .errors import Errors
from .vm_shutdown_response_data import VmShutdownResponseData

__all__ = ["VmShutdownResponse"]

@dataclass
class VmShutdownResponse:
    """
    VmShutdownResponse dataclass
    
    Args:
        data_ (VmShutdownResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmShutdownResponseData | None = None  # Maps from 'data'
    errors: Errors | None = None
    success: bool | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "data": "data_",
            "errors": "errors",
            "success": "success",
        }
        key_transform_with_dump = {
            "data_": "data",
            "errors": "errors",
            "success": "success",
        }
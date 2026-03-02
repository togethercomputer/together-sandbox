from dataclasses import dataclass

from .errors import Errors
from .vm_shutdown_response_data_2 import VmShutdownResponseData2

__all__ = ["VmShutdownResponse2"]

@dataclass
class VmShutdownResponse2:
    """
    VmShutdownResponse2 dataclass
    
    Args:
        data_ (VmShutdownResponseData2 | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmShutdownResponseData2 | None = None  # Maps from 'data'
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
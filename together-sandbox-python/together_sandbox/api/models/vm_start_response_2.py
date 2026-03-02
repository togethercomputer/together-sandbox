from dataclasses import dataclass

from .errors import Errors
from .vm_start_response_data_2 import VmStartResponseData2

__all__ = ["VmStartResponse2"]

@dataclass
class VmStartResponse2:
    """
    VmStartResponse2 dataclass
    
    Args:
        data_ (VmStartResponseData2 | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmStartResponseData2 | None = None  # Maps from 'data'
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
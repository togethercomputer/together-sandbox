from dataclasses import dataclass

from .errors import Errors
from .vm_start_response_data import VmStartResponseData

__all__ = ["VmStartResponse"]

@dataclass
class VmStartResponse:
    """
    VmStartResponse dataclass
    
    Args:
        data_ (VmStartResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmStartResponseData | None = None  # Maps from 'data'
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
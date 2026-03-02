from dataclasses import dataclass

from .errors import Errors
from .vm_delete_response_data import VmDeleteResponseData

__all__ = ["VmDeleteResponse"]

@dataclass
class VmDeleteResponse:
    """
    VmDeleteResponse dataclass
    
    Args:
        data_ (VmDeleteResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmDeleteResponseData | None = None  # Maps from 'data'
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
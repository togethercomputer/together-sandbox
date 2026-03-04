from dataclasses import dataclass

from .errors import Errors
from .vm_update_specs_response_data import VmUpdateSpecsResponseData

__all__ = ["VmUpdateSpecsResponse"]

@dataclass
class VmUpdateSpecsResponse:
    """
    VmUpdateSpecsResponse dataclass
    
    Args:
        data_ (VmUpdateSpecsResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmUpdateSpecsResponseData | None = None  # Maps from 'data'
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
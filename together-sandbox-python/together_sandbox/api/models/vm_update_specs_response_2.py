from dataclasses import dataclass

from .errors import Errors
from .vm_update_specs_response_data_2 import VmUpdateSpecsResponseData2

__all__ = ["VmUpdateSpecsResponse2"]

@dataclass
class VmUpdateSpecsResponse2:
    """
    VmUpdateSpecsResponse2 dataclass
    
    Args:
        data_ (VmUpdateSpecsResponseData2 | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmUpdateSpecsResponseData2 | None = None  # Maps from 'data'
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
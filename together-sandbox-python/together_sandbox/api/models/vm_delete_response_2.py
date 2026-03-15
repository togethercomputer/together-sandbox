from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .vm_delete_response_data_2 import VmDeleteResponseData2

__all__ = ["VmDeleteResponse2"]

@dataclass
class VmDeleteResponse2:
    """
    VmDeleteResponse2 dataclass
    
    Args:
        data_ (VmDeleteResponseData2 | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmDeleteResponseData2 | None = None  # Maps from 'data'
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
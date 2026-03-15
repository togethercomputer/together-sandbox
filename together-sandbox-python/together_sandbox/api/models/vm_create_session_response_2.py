from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .vm_create_session_response_data_2 import VmCreateSessionResponseData2

__all__ = ["VmCreateSessionResponse2"]

@dataclass
class VmCreateSessionResponse2:
    """
    VmCreateSessionResponse2 dataclass
    
    Args:
        data_ (VmCreateSessionResponseData2 | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmCreateSessionResponseData2 | None = None  # Maps from 'data'
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
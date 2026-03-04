from dataclasses import dataclass

from .errors import Errors
from .vm_create_session_response_data import VmCreateSessionResponseData

__all__ = ["VmCreateSessionResponse"]

@dataclass
class VmCreateSessionResponse:
    """
    VmCreateSessionResponse dataclass
    
    Args:
        data_ (VmCreateSessionResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmCreateSessionResponseData | None = None  # Maps from 'data'
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
from dataclasses import dataclass

from .errors import Errors
from .vm_create_tag_response_data import VmCreateTagResponseData

__all__ = ["VmCreateTagResponse"]

@dataclass
class VmCreateTagResponse:
    """
    VmCreateTagResponse dataclass
    
    Args:
        data_ (VmCreateTagResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmCreateTagResponseData | None = None  # Maps from 'data'
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
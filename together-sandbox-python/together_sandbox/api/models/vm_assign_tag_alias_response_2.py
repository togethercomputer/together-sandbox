from dataclasses import dataclass

from .errors import Errors
from .vm_assign_tag_alias_response_data_2 import VmAssignTagAliasResponseData2

__all__ = ["VmAssignTagAliasResponse2"]

@dataclass
class VmAssignTagAliasResponse2:
    """
    VmAssignTagAliasResponse2 dataclass
    
    Args:
        data_ (VmAssignTagAliasResponseData2 | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmAssignTagAliasResponseData2 | None = None  # Maps from 'data'
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
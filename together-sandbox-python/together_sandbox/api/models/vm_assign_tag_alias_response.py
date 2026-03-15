from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .vm_assign_tag_alias_response_data import VmAssignTagAliasResponseData

__all__ = ["VmAssignTagAliasResponse"]

@dataclass
class VmAssignTagAliasResponse:
    """
    VmAssignTagAliasResponse dataclass
    
    Args:
        data_ (VmAssignTagAliasResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmAssignTagAliasResponseData | None = None  # Maps from 'data'
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
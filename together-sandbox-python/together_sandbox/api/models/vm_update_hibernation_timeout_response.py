from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .vm_update_hibernation_timeout_response_data import VmUpdateHibernationTimeoutResponseData

__all__ = ["VmUpdateHibernationTimeoutResponse"]

@dataclass
class VmUpdateHibernationTimeoutResponse:
    """
    VmUpdateHibernationTimeoutResponse dataclass
    
    Args:
        data_ (VmUpdateHibernationTimeoutResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmUpdateHibernationTimeoutResponseData | None = None  # Maps from 'data'
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
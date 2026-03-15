from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .vm_list_running_v_ms_response_data import VmListRunningVMsResponseData

__all__ = ["VmListRunningVMsResponse"]

@dataclass
class VmListRunningVMsResponse:
    """
    VmListRunningVMsResponse dataclass
    
    Args:
        data_ (VmListRunningVMsResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmListRunningVMsResponseData | None = None  # Maps from 'data'
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
from dataclasses import dataclass

from .errors import Errors
from .sandbox_list_response_data import SandboxListResponseData

__all__ = ["SandboxListResponse"]

@dataclass
class SandboxListResponse:
    """
    SandboxListResponse dataclass
    
    Args:
        data_ (SandboxListResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: SandboxListResponseData | None = None  # Maps from 'data'
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
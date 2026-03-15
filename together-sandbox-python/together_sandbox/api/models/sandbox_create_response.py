from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .sandbox_create_response_data import SandboxCreateResponseData

__all__ = ["SandboxCreateResponse"]

@dataclass
class SandboxCreateResponse:
    """
    SandboxCreateResponse dataclass
    
    Args:
        data_ (SandboxCreateResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: SandboxCreateResponseData | None = None  # Maps from 'data'
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
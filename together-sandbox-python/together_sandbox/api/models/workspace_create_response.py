from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .workspace_create_response_data import WorkspaceCreateResponseData

__all__ = ["WorkspaceCreateResponse"]

@dataclass
class WorkspaceCreateResponse:
    """
    WorkspaceCreateResponse dataclass
    
    Args:
        data_ (WorkspaceCreateResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: WorkspaceCreateResponseData | None = None  # Maps from 'data'
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
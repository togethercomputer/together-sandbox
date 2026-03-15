from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .preview_token_list_response_data import PreviewTokenListResponseData

__all__ = ["PreviewTokenListResponse"]

@dataclass
class PreviewTokenListResponse:
    """
    PreviewTokenListResponse dataclass
    
    Args:
        data_ (PreviewTokenListResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: PreviewTokenListResponseData | None = None  # Maps from 'data'
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
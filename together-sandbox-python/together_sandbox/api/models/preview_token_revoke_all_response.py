from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .preview_token_revoke_all_response_data import PreviewTokenRevokeAllResponseData

__all__ = ["PreviewTokenRevokeAllResponse"]

@dataclass
class PreviewTokenRevokeAllResponse:
    """
    PreviewTokenRevokeAllResponse dataclass
    
    Args:
        data_ (PreviewTokenRevokeAllResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: PreviewTokenRevokeAllResponseData | None = None  # Maps from 'data'
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
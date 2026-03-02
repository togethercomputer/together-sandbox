from dataclasses import dataclass

from .errors import Errors
from .preview_token_create_response_data import PreviewTokenCreateResponseData

__all__ = ["PreviewTokenCreateResponse"]

@dataclass
class PreviewTokenCreateResponse:
    """
    PreviewTokenCreateResponse dataclass
    
    Args:
        data_ (PreviewTokenCreateResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: PreviewTokenCreateResponseData | None = None  # Maps from 'data'
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
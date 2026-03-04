from dataclasses import dataclass

from .errors import Errors
from .preview_token_update_response_data import PreviewTokenUpdateResponseData

__all__ = ["PreviewTokenUpdateResponse"]

@dataclass
class PreviewTokenUpdateResponse:
    """
    PreviewTokenUpdateResponse dataclass
    
    Args:
        data_ (PreviewTokenUpdateResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: PreviewTokenUpdateResponseData | None = None  # Maps from 'data'
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
from dataclasses import dataclass

from .errors import Errors
from .preview_host_list_response_data import PreviewHostListResponseData

__all__ = ["PreviewHostListResponse"]

@dataclass
class PreviewHostListResponse:
    """
    PreviewHostListResponse dataclass
    
    Args:
        data_ (PreviewHostListResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: PreviewHostListResponseData | None = None  # Maps from 'data'
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
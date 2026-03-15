from __future__ import annotations

from dataclasses import dataclass

from .errors import Errors
from .template_create_response_data import TemplateCreateResponseData

__all__ = ["TemplateCreateResponse"]

@dataclass
class TemplateCreateResponse:
    """
    TemplateCreateResponse dataclass
    
    Args:
        data_ (TemplateCreateResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: TemplateCreateResponseData | None = None  # Maps from 'data'
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
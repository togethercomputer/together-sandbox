from dataclasses import dataclass

from .response_errors import ResponseErrors

__all__ = ["Response"]

@dataclass
class Response:
    """
    Response dataclass
    
    Args:
        errors (ResponseErrors | None)
                                 : 
        success (bool | None)    : 
    """
    errors: ResponseErrors | None = None
    success: bool | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "errors": "errors",
            "success": "success",
        }
        key_transform_with_dump = {
            "errors": "errors",
            "success": "success",
        }
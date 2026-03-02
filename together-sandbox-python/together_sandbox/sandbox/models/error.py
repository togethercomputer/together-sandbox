from dataclasses import dataclass

__all__ = ["Error"]

@dataclass
class Error:
    """
    Error dataclass
    
    Args:
        code (int)               : 
        message (str)            : 
    """
    code: int
    message: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "code": "code",
            "message": "message",
        }
        key_transform_with_dump = {
            "code": "code",
            "message": "message",
        }
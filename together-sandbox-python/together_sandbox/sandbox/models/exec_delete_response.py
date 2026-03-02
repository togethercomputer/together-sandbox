from dataclasses import dataclass

__all__ = ["ExecDeleteResponse"]

@dataclass
class ExecDeleteResponse:
    """
    ExecDeleteResponse dataclass
    
    Args:
        message (str)            : Deletion confirmation message
    """
    message: str  # Deletion confirmation message
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "message": "message",
        }
        key_transform_with_dump = {
            "message": "message",
        }
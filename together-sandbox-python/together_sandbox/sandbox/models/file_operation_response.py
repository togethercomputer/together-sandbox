from dataclasses import dataclass

__all__ = ["FileOperationResponse"]

@dataclass
class FileOperationResponse:
    """
    FileOperationResponse dataclass
    
    Args:
        message (str)            : Operation result message
        path (str)               : File or directory path
    """
    message: str  # Operation result message
    path: str  # File or directory path
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "message": "message",
            "path": "path",
        }
        key_transform_with_dump = {
            "message": "message",
            "path": "path",
        }
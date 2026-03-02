from dataclasses import dataclass

__all__ = ["FileReadResponse"]

@dataclass
class FileReadResponse:
    """
    FileReadResponse dataclass
    
    Args:
        content (str)            : File content
        path (str)               : File path
    """
    content: str  # File content
    path: str  # File path
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "content": "content",
            "path": "path",
        }
        key_transform_with_dump = {
            "content": "content",
            "path": "path",
        }
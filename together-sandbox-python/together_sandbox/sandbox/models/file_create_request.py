from dataclasses import dataclass

__all__ = ["FileCreateRequest"]

@dataclass
class FileCreateRequest:
    """
    FileCreateRequest dataclass
    
    Args:
        content (str | None)     : File content to create
    """
    content: str | None = None  # File content to create
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "content": "content",
        }
        key_transform_with_dump = {
            "content": "content",
        }
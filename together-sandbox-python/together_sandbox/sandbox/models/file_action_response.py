from dataclasses import dataclass

__all__ = ["FileActionResponse"]

@dataclass
class FileActionResponse:
    """
    FileActionResponse dataclass
    
    Args:
        from_ (str)              : Source path (maps from 'from')
        message (str)            : Operation result message
        to (str)                 : Destination path
    """
    from_: str  # Source path (maps from 'from')
    message: str  # Operation result message
    to: str  # Destination path
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "from": "from_",
            "message": "message",
            "to": "to",
        }
        key_transform_with_dump = {
            "from_": "from",
            "message": "message",
            "to": "to",
        }
from dataclasses import dataclass

__all__ = ["TaskPreview"]

@dataclass
class TaskPreview:
    """
    TaskPreview dataclass
    
    Args:
        port (int)               : 
    """
    port: int
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "port": "port",
        }
        key_transform_with_dump = {
            "port": "port",
        }
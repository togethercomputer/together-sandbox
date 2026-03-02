from dataclasses import dataclass

__all__ = ["SandboxCreateResponseData"]

@dataclass
class SandboxCreateResponseData:
    """
    SandboxCreateResponseData dataclass
    
    Args:
        alias (str)              : 
        id_ (str)                : Maps from 'id'
        title (str | None)       : 
    """
    alias: str
    id_: str  # Maps from 'id'
    title: str | None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "alias": "alias",
            "id": "id_",
            "title": "title",
        }
        key_transform_with_dump = {
            "alias": "alias",
            "id_": "id",
            "title": "title",
        }
from dataclasses import dataclass

__all__ = ["WorkspaceCreateResponseData"]

@dataclass
class WorkspaceCreateResponseData:
    """
    WorkspaceCreateResponseData dataclass
    
    Args:
        id_ (str)                : Maps from 'id'
        name (str)               : 
    """
    id_: str  # Maps from 'id'
    name: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "id": "id_",
            "name": "name",
        }
        key_transform_with_dump = {
            "id_": "id",
            "name": "name",
        }
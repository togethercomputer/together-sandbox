from __future__ import annotations

from dataclasses import dataclass

__all__ = ["VmAssignTagAliasRequest"]

@dataclass
class VmAssignTagAliasRequest:
    """
    Assign a tag alias to a VM
    
    Args:
        tag_id (str)             : 
    """
    tag_id: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "tag_id": "tag_id",
        }
        key_transform_with_dump = {
            "tag_id": "tag_id",
        }
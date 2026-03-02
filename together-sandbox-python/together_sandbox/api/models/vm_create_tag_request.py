from dataclasses import dataclass
from typing import List

__all__ = ["VmCreateTagRequest"]

@dataclass
class VmCreateTagRequest:
    """
    Create a tag for a list of VM IDs
    
    Args:
        vm_ids (List[str])       : 
    """
    vm_ids: List[str]
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "vm_ids": "vm_ids",
        }
        key_transform_with_dump = {
            "vm_ids": "vm_ids",
        }
from dataclasses import dataclass
from typing import List

__all__ = ["PreviewHostRequest"]

@dataclass
class PreviewHostRequest:
    """
    PreviewHostRequest dataclass
    
    Args:
        hosts (List[str])        : 
    """
    hosts: List[str]
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "hosts": "hosts",
        }
        key_transform_with_dump = {
            "hosts": "hosts",
        }
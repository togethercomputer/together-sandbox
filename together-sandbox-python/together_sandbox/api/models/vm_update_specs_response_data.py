from dataclasses import dataclass

__all__ = ["VmUpdateSpecsResponseData"]

@dataclass
class VmUpdateSpecsResponseData:
    """
    VmUpdateSpecsResponseData dataclass
    
    Args:
        id_ (str)                : Maps from 'id'
        tier (str)               : 
    """
    id_: str  # Maps from 'id'
    tier: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "id": "id_",
            "tier": "tier",
        }
        key_transform_with_dump = {
            "id_": "id",
            "tier": "tier",
        }
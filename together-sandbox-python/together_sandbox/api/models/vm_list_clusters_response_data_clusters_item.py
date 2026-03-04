from dataclasses import dataclass

__all__ = ["VmListClustersResponseDataClustersItem"]

@dataclass
class VmListClustersResponseDataClustersItem:
    """
    VmListClustersResponseDataClustersItem dataclass
    
    Args:
        host (str)               : 
        slug (str)               : 
    """
    host: str
    slug: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "host": "host",
            "slug": "slug",
        }
        key_transform_with_dump = {
            "host": "host",
            "slug": "slug",
        }
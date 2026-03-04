from dataclasses import dataclass

__all__ = ["MetaInformationRateLimitsConcurrentVms"]

@dataclass
class MetaInformationRateLimitsConcurrentVms:
    """
    MetaInformationRateLimitsConcurrentVms dataclass
    
    Args:
        limit (int | None)       : 
        remaining (int | None)   : 
    """
    limit: int | None = None
    remaining: int | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "limit": "limit",
            "remaining": "remaining",
        }
        key_transform_with_dump = {
            "limit": "limit",
            "remaining": "remaining",
        }
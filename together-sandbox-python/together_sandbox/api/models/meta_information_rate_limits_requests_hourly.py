from __future__ import annotations

from dataclasses import dataclass

__all__ = ["MetaInformationRateLimitsRequestsHourly"]

@dataclass
class MetaInformationRateLimitsRequestsHourly:
    """
    MetaInformationRateLimitsRequestsHourly dataclass
    
    Args:
        limit (int | None)       : 
        remaining (int | None)   : 
        reset (int | None)       : 
    """
    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "limit": "limit",
            "remaining": "remaining",
            "reset": "reset",
        }
        key_transform_with_dump = {
            "limit": "limit",
            "remaining": "remaining",
            "reset": "reset",
        }
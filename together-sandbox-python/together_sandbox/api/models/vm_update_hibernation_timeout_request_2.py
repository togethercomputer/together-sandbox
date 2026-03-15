from __future__ import annotations

from dataclasses import dataclass

__all__ = ["VmUpdateHibernationTimeoutRequest2"]

@dataclass
class VmUpdateHibernationTimeoutRequest2:
    """
    VmUpdateHibernationTimeoutRequest2 dataclass
    
    Args:
        hibernation_timeout_seconds (int)
                                 : The new hibernation timeout in seconds.  Must be greater
                                   than 0 and less than or equal to 86400 (24 hours).
    """
    hibernation_timeout_seconds: int  # The new hibernation timeout in seconds.  Must be greater than 0 and less than or equal to 86400 (24 hours). 
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "hibernation_timeout_seconds": "hibernation_timeout_seconds",
        }
        key_transform_with_dump = {
            "hibernation_timeout_seconds": "hibernation_timeout_seconds",
        }
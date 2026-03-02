from dataclasses import dataclass

__all__ = ["VmUpdateHibernationTimeoutResponseData"]

@dataclass
class VmUpdateHibernationTimeoutResponseData:
    """
    VmUpdateHibernationTimeoutResponseData dataclass
    
    Args:
        hibernation_timeout_seconds (int)
                                 : 
        id_ (str)                : Maps from 'id'
    """
    hibernation_timeout_seconds: int
    id_: str  # Maps from 'id'
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "hibernation_timeout_seconds": "hibernation_timeout_seconds",
            "id": "id_",
        }
        key_transform_with_dump = {
            "hibernation_timeout_seconds": "hibernation_timeout_seconds",
            "id_": "id",
        }
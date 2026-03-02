from dataclasses import dataclass

from .errors import Errors
from .vm_list_clusters_response_data import VmListClustersResponseData

__all__ = ["VmListClustersResponse"]

@dataclass
class VmListClustersResponse:
    """
    VmListClustersResponse dataclass
    
    Args:
        data_ (VmListClustersResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmListClustersResponseData | None = None  # Maps from 'data'
    errors: Errors | None = None
    success: bool | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "data": "data_",
            "errors": "errors",
            "success": "success",
        }
        key_transform_with_dump = {
            "data_": "data",
            "errors": "errors",
            "success": "success",
        }
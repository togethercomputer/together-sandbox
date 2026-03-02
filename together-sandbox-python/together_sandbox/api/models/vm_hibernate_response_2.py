from dataclasses import dataclass

from .errors import Errors
from .vm_hibernate_response_data_2 import VmHibernateResponseData2

__all__ = ["VmHibernateResponse2"]

@dataclass
class VmHibernateResponse2:
    """
    VmHibernateResponse2 dataclass
    
    Args:
        data_ (VmHibernateResponseData2 | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: VmHibernateResponseData2 | None = None  # Maps from 'data'
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
from dataclasses import dataclass

from .errors import Errors
from .sandbox_fork_response_data import SandboxForkResponseData

__all__ = ["SandboxForkResponse"]

@dataclass
class SandboxForkResponse:
    """
    SandboxForkResponse dataclass
    
    Args:
        data_ (SandboxForkResponseData | None)
                                 : Maps from 'data'
        errors (Errors | None)   : 
        success (bool | None)    : 
    """
    data_: SandboxForkResponseData | None = None  # Maps from 'data'
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
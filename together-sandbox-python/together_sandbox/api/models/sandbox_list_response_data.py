from dataclasses import dataclass
from typing import List

from .sandbox import Sandbox
from .sandbox_list_response_data_pagination import SandboxListResponseDataPagination

__all__ = ["SandboxListResponseData"]

@dataclass
class SandboxListResponseData:
    """
    SandboxListResponseData dataclass
    
    Args:
        pagination (SandboxListResponseDataPagination)
                                 : 
        sandboxes (List[Sandbox]): 
    """
    pagination: SandboxListResponseDataPagination
    sandboxes: List[Sandbox]
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "pagination": "pagination",
            "sandboxes": "sandboxes",
        }
        key_transform_with_dump = {
            "pagination": "pagination",
            "sandboxes": "sandboxes",
        }
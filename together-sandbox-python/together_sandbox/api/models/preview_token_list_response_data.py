from dataclasses import dataclass
from typing import List

from .preview_token import PreviewToken

__all__ = ["PreviewTokenListResponseData"]

@dataclass
class PreviewTokenListResponseData:
    """
    PreviewTokenListResponseData dataclass
    
    Args:
        sandbox_id (str)         : 
        tokens (List[PreviewToken])
                                 : 
    """
    sandbox_id: str
    tokens: List[PreviewToken]
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "sandbox_id": "sandbox_id",
            "tokens": "tokens",
        }
        key_transform_with_dump = {
            "sandbox_id": "sandbox_id",
            "tokens": "tokens",
        }
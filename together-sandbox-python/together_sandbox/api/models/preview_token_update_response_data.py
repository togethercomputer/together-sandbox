from dataclasses import dataclass

from .preview_token import PreviewToken

__all__ = ["PreviewTokenUpdateResponseData"]

@dataclass
class PreviewTokenUpdateResponseData:
    """
    PreviewTokenUpdateResponseData dataclass
    
    Args:
        sandbox_id (str)         : 
        token (PreviewToken)     : 
    """
    sandbox_id: str
    token: PreviewToken
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "sandbox_id": "sandbox_id",
            "token": "token",
        }
        key_transform_with_dump = {
            "sandbox_id": "sandbox_id",
            "token": "token",
        }
from dataclasses import dataclass

from .preview_token_create_response_data_token import PreviewTokenCreateResponseDataToken

__all__ = ["PreviewTokenCreateResponseData"]

@dataclass
class PreviewTokenCreateResponseData:
    """
    PreviewTokenCreateResponseData dataclass
    
    Args:
        sandbox_id (str)         : 
        token (PreviewTokenCreateResponseDataToken)
                                 : 
    """
    sandbox_id: str
    token: PreviewTokenCreateResponseDataToken
    
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
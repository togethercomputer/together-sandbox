from dataclasses import dataclass

__all__ = ["PreviewTokenCreateResponseDataToken"]

@dataclass
class PreviewTokenCreateResponseDataToken:
    """
    PreviewTokenCreateResponseDataToken dataclass
    
    Args:
        expires_at (str | None)  : 
        last_used_at (str | None): 
        token (str)              : 
        token_id (str)           : 
        token_prefix (str)       : 
    """
    expires_at: str | None
    last_used_at: str | None
    token: str
    token_id: str
    token_prefix: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "expires_at": "expires_at",
            "last_used_at": "last_used_at",
            "token": "token",
            "token_id": "token_id",
            "token_prefix": "token_prefix",
        }
        key_transform_with_dump = {
            "expires_at": "expires_at",
            "last_used_at": "last_used_at",
            "token": "token",
            "token_id": "token_id",
            "token_prefix": "token_prefix",
        }
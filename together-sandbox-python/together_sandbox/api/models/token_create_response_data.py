from __future__ import annotations

from dataclasses import dataclass
from typing import List

__all__ = ["TokenCreateResponseData"]

@dataclass
class TokenCreateResponseData:
    """
    TokenCreateResponseData dataclass
    
    Args:
        description (str | None) : 
        expires_at (str | None)  : 
        scopes (List[str])       : 
        team_id (str)            : 
        token (str)              : 
        token_id (str)           : 
    """
    description: str | None
    expires_at: str | None
    scopes: List[str]
    team_id: str
    token: str
    token_id: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "description": "description",
            "expires_at": "expires_at",
            "scopes": "scopes",
            "team_id": "team_id",
            "token": "token",
            "token_id": "token_id",
        }
        key_transform_with_dump = {
            "description": "description",
            "expires_at": "expires_at",
            "scopes": "scopes",
            "team_id": "team_id",
            "token": "token",
            "token_id": "token_id",
        }
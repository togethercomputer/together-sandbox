from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

__all__ = ["TokenUpdateResponseData"]

@dataclass
class TokenUpdateResponseData:
    """
    TokenUpdateResponseData dataclass
    
    Args:
        description (str | None) : 
        scopes (List[str])       : 
        team_id (str)            : 
        token_id (str)           : 
        expires_at (datetime | None)
                                 : 
    """
    description: str | None
    scopes: List[str]
    team_id: str
    token_id: str
    expires_at: datetime | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "description": "description",
            "expires_at": "expires_at",
            "scopes": "scopes",
            "team_id": "team_id",
            "token_id": "token_id",
        }
        key_transform_with_dump = {
            "description": "description",
            "expires_at": "expires_at",
            "scopes": "scopes",
            "team_id": "team_id",
            "token_id": "token_id",
        }
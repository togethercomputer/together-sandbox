from dataclasses import dataclass
from typing import List

from uuid import UUID

__all__ = ["MetaInformationAuth"]

@dataclass
class MetaInformationAuth:
    """
    Meta information about the current authentication context
    
    Args:
        scopes (List[str])       : 
        team (UUID | None)       : 
        version (str)            : 
    """
    scopes: List[str]
    team: UUID | None
    version: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "scopes": "scopes",
            "team": "team",
            "version": "version",
        }
        key_transform_with_dump = {
            "scopes": "scopes",
            "team": "team",
            "version": "version",
        }
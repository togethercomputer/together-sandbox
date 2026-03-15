from __future__ import annotations

from dataclasses import dataclass

__all__ = ["MetaInformationApi"]

@dataclass
class MetaInformationApi:
    """
    Meta information about the CodeSandbox API
    
    Args:
        latest_version (str)     : 
        name (str)               : 
    """
    latest_version: str
    name: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "latest_version": "latest_version",
            "name": "name",
        }
        key_transform_with_dump = {
            "latest_version": "latest_version",
            "name": "name",
        }
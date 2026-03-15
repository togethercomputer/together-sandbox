from __future__ import annotations

from dataclasses import dataclass

__all__ = ["WorkspaceCreateRequest"]

@dataclass
class WorkspaceCreateRequest:
    """
    WorkspaceCreateRequest dataclass
    
    Args:
        name (str)               : Name for the new workspace. Maximum length 64 characters.
    """
    name: str  # Name for the new workspace. Maximum length 64 characters.
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "name": "name",
        }
        key_transform_with_dump = {
            "name": "name",
        }
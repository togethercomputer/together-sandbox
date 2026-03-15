from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from .sandbox_settings import SandboxSettings

__all__ = ["Sandbox"]

@dataclass
class Sandbox:
    """
    Sandbox dataclass
    
    Args:
        created_at (datetime)    : 
        id_ (str)                : Maps from 'id'
        is_frozen (bool)         : 
        privacy (int)            : 
        settings (SandboxSettings): 
        tags (List[str])         : 
        updated_at (datetime)    : 
        description (str | None) : 
        title (str | None)       : 
    """
    created_at: datetime
    id_: str  # Maps from 'id'
    is_frozen: bool
    privacy: int
    settings: SandboxSettings
    tags: List[str]
    updated_at: datetime
    description: str | None = None
    title: str | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "created_at": "created_at",
            "description": "description",
            "id": "id_",
            "is_frozen": "is_frozen",
            "privacy": "privacy",
            "settings": "settings",
            "tags": "tags",
            "title": "title",
            "updated_at": "updated_at",
        }
        key_transform_with_dump = {
            "created_at": "created_at",
            "description": "description",
            "id_": "id",
            "is_frozen": "is_frozen",
            "privacy": "privacy",
            "settings": "settings",
            "tags": "tags",
            "title": "title",
            "updated_at": "updated_at",
        }
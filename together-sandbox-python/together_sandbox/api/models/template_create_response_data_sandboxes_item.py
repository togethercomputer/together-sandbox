from __future__ import annotations

from dataclasses import dataclass

__all__ = ["TemplateCreateResponseDataSandboxesItem"]

@dataclass
class TemplateCreateResponseDataSandboxesItem:
    """
    TemplateCreateResponseDataSandboxesItem dataclass
    
    Args:
        cluster (str)            : 
        id_ (str)                : Maps from 'id'
    """
    cluster: str
    id_: str  # Maps from 'id'
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "cluster": "cluster",
            "id": "id_",
        }
        key_transform_with_dump = {
            "cluster": "cluster",
            "id_": "id",
        }
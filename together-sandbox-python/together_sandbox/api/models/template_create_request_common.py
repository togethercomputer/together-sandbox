from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .template_create_request_common_image import TemplateCreateRequestCommonImage

__all__ = ["TemplateCreateRequestCommon"]

@dataclass
class TemplateCreateRequestCommon:
    """
    TemplateCreateRequestCommon dataclass
    
    Args:
        fork_of (str)            : Short ID of the sandbox to fork. (maps from 'forkOf')
        description (str | None) : Template description. Maximum 255 characters. Defaults to
                                   description of original sandbox.
        image (TemplateCreateRequestCommonImage | None)
                                 : Container image to use as template
        tags (List[str] | None)  : Tags to set on the new sandbox, if any. Will not inherit
                                   tags from the source sandbox.
        title (str | None)       : Template title. Maximum 255 characters. Defaults to title
                                   of original sandbox with (forked).
    """
    fork_of: str  # Short ID of the sandbox to fork. (maps from 'forkOf')
    description: str | None = "[Template description]"  # Template description. Maximum 255 characters. Defaults to description of original sandbox.
    image: TemplateCreateRequestCommonImage | None = None  # Container image to use as template
    tags: List[str] | None = field(default_factory=list)  # Tags to set on the new sandbox, if any. Will not inherit tags from the source sandbox.
    title: str | None = "[Template title]"  # Template title. Maximum 255 characters. Defaults to title of original sandbox with (forked).
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "description": "description",
            "forkOf": "fork_of",
            "image": "image",
            "tags": "tags",
            "title": "title",
        }
        key_transform_with_dump = {
            "description": "description",
            "fork_of": "forkOf",
            "image": "image",
            "tags": "tags",
            "title": "title",
        }
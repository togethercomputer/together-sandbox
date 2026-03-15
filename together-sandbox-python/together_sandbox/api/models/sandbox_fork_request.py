from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .sandbox_fork_request_start_options import SandboxForkRequestStartOptions

__all__ = ["SandboxForkRequest"]

@dataclass
class SandboxForkRequest:
    """
    SandboxForkRequest dataclass
    
    Args:
        description (str | None) : Sandbox description. Maximum 255 characters. Defaults to
                                   description of original sandbox.
        is_frozen (bool | None)  : Sandbox frozen status. When true, edits to the sandbox
                                   are restricted. Defaults to frozen status of the original
                                   sandbox.
        path (str | None)        : Path to the collection where the new sandbox should be
                                   stored. Defaults to "/". If no collection exists at the
                                   given path, it will be created.
        privacy (int | None)     : Sandbox privacy. 0 for public, 1 for unlisted, and 2 for
                                   private. Subject to the minimum privacy restrictions of
                                   the workspace. Defaults to the privacy of the original
                                   sandbox.
        private_preview (bool | None)
                                 : Determines whether the preview of a private sandbox is
                                   private or public. Has no effect on public or unlisted
                                   sandboxes; their previews are always publicly accessible
        start_options (SandboxForkRequestStartOptions | None)
                                 : Optional VM start configuration. If provided, the sandbox
                                   VM will be started immediately after creation.
        tags (List[str] | None)  : Tags to set on the new sandbox, if any. Will not inherit
                                   tags from the source sandbox.
        title (str | None)       : Sandbox title. Maximum 255 characters. Defaults to title
                                   of original sandbox with (forked).
    """
    description: str | None = "[Original description]"  # Sandbox description. Maximum 255 characters. Defaults to description of original sandbox.
    is_frozen: bool | None = False  # Sandbox frozen status. When true, edits to the sandbox are restricted. Defaults to frozen status of the original sandbox.
    path: str | None = "/"  # Path to the collection where the new sandbox should be stored. Defaults to "/". If no collection exists at the given path, it will be created.
    privacy: int | None = 0  # Sandbox privacy. 0 for public, 1 for unlisted, and 2 for private. Subject to the minimum privacy restrictions of the workspace. Defaults to the privacy of the original sandbox.
    private_preview: bool | None = None  # Determines whether the preview of a private sandbox is private or public. Has no effect on public or unlisted sandboxes; their previews are always publicly accessible
    start_options: SandboxForkRequestStartOptions | None = None  # Optional VM start configuration. If provided, the sandbox VM will be started immediately after creation.
    tags: List[str] | None = field(default_factory=list)  # Tags to set on the new sandbox, if any. Will not inherit tags from the source sandbox.
    title: str | None = "[Original title]"  # Sandbox title. Maximum 255 characters. Defaults to title of original sandbox with (forked).
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "description": "description",
            "is_frozen": "is_frozen",
            "path": "path",
            "privacy": "privacy",
            "private_preview": "private_preview",
            "start_options": "start_options",
            "tags": "tags",
            "title": "title",
        }
        key_transform_with_dump = {
            "description": "description",
            "is_frozen": "is_frozen",
            "path": "path",
            "privacy": "privacy",
            "private_preview": "private_preview",
            "start_options": "start_options",
            "tags": "tags",
            "title": "title",
        }
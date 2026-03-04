from dataclasses import dataclass, field
from typing import List

from .sandbox_create_request_files import SandboxCreateRequestFiles
from .sandbox_create_request_npm_dependencies import SandboxCreateRequestNpmDependencies
from .sandbox_create_request_runtime import SandboxCreateRequestRuntime
from .sandbox_create_request_settings import SandboxCreateRequestSettings

__all__ = ["SandboxCreateRequest"]

@dataclass
class SandboxCreateRequest:
    """
    SandboxCreateRequest dataclass
    
    Args:
        files (SandboxCreateRequestFiles)
                                 : Map of `path => file` where each file is a map.
        description (str | None) : Optional text description of the sandbox. Defaults to no
                                   description.
        entry (str | None)       : Filename of the entrypoint of the sandbox.
        external_resources (List[str] | None)
                                 : Array of strings with external resources to load.
        is_frozen (bool | None)  : Whether changes to the sandbox are disallowed. Defaults
                                   to `false`.
        npm_dependencies (SandboxCreateRequestNpmDependencies | None)
                                 : Map of dependencies and their version specifications.
        path (str | None)        : Path to the collection where the new sandbox should be
                                   stored. Defaults to "/". If no collection exists at the
                                   given path, it will be created.
        privacy (int | None)     : 0 for public, 1 for unlisted, and 2 for private. Privacy
                                   is subject to certain restrictions (team minimum setting,
                                   drafts must be private, etc.). Defaults to public.
        private_preview (bool | None)
                                 : Determines whether the preview of a private sandbox is
                                   private or public. Has no effect on public or unlisted
                                   sandboxes; their previews are always publicly accessible
        runtime (SandboxCreateRequestRuntime | None)
                                 : Runtime to use for the sandbox. Defaults to `"browser"`.
        settings (SandboxCreateRequestSettings | None)
                                 : Sandbox settings.
        tags (List[str] | None)  : List of string tags to apply to the sandbox. Only the
                                   first ten will be used. Defaults to no tags.
        template (str | None)    : Name of the template from which the sandbox is derived
                                   (for example, `"static"`).
        title (str | None)       : Sandbox title. Maximum 255 characters. Defaults to no
                                   title.
    """
    files: SandboxCreateRequestFiles  # Map of `path => file` where each file is a map.
    description: str | None = None  # Optional text description of the sandbox. Defaults to no description.
    entry: str | None = None  # Filename of the entrypoint of the sandbox.
    external_resources: List[str] | None = field(default_factory=list)  # Array of strings with external resources to load.
    is_frozen: bool | None = False  # Whether changes to the sandbox are disallowed. Defaults to `false`.
    npm_dependencies: SandboxCreateRequestNpmDependencies | None = None  # Map of dependencies and their version specifications.
    path: str | None = "/"  # Path to the collection where the new sandbox should be stored. Defaults to "/". If no collection exists at the given path, it will be created.
    privacy: int | None = 0  # 0 for public, 1 for unlisted, and 2 for private. Privacy is subject to certain restrictions (team minimum setting, drafts must be private, etc.). Defaults to public.
    private_preview: bool | None = None  # Determines whether the preview of a private sandbox is private or public. Has no effect on public or unlisted sandboxes; their previews are always publicly accessible
    runtime: SandboxCreateRequestRuntime | None = "browser"  # Runtime to use for the sandbox. Defaults to `"browser"`.
    settings: SandboxCreateRequestSettings | None = None  # Sandbox settings.
    tags: List[str] | None = field(default_factory=list)  # List of string tags to apply to the sandbox. Only the first ten will be used. Defaults to no tags.
    template: str | None = None  # Name of the template from which the sandbox is derived (for example, `"static"`).
    title: str | None = ""  # Sandbox title. Maximum 255 characters. Defaults to no title.
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "description": "description",
            "entry": "entry",
            "external_resources": "external_resources",
            "files": "files",
            "is_frozen": "is_frozen",
            "npm_dependencies": "npm_dependencies",
            "path": "path",
            "privacy": "privacy",
            "private_preview": "private_preview",
            "runtime": "runtime",
            "settings": "settings",
            "tags": "tags",
            "template": "template",
            "title": "title",
        }
        key_transform_with_dump = {
            "description": "description",
            "entry": "entry",
            "external_resources": "external_resources",
            "files": "files",
            "is_frozen": "is_frozen",
            "npm_dependencies": "npm_dependencies",
            "path": "path",
            "privacy": "privacy",
            "private_preview": "private_preview",
            "runtime": "runtime",
            "settings": "settings",
            "tags": "tags",
            "template": "template",
            "title": "title",
        }
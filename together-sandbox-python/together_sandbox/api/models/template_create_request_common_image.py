from dataclasses import dataclass

__all__ = ["TemplateCreateRequestCommonImage"]

@dataclass
class TemplateCreateRequestCommonImage:
    """
    Container image to use as template
    
    Args:
        name (str)               : The image name (for example 'nginx').
        architecture (str | None): The architecture of the image. Required for multi-
                                   platform images
        registry (str | None)    : The container registry where the image is stored.
        repository (str | None)  : The repository or namespace where the image is stored.
        tag (str | None)         : The image tag.
    """
    name: str  # The image name (for example 'nginx').
    architecture: str | None = None  # The architecture of the image. Required for multi-platform images
    registry: str | None = "docker.io"  # The container registry where the image is stored.
    repository: str | None = "library"  # The repository or namespace where the image is stored.
    tag: str | None = "latest"  # The image tag.
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "architecture": "architecture",
            "name": "name",
            "registry": "registry",
            "repository": "repository",
            "tag": "tag",
        }
        key_transform_with_dump = {
            "architecture": "architecture",
            "name": "name",
            "registry": "registry",
            "repository": "repository",
            "tag": "tag",
        }
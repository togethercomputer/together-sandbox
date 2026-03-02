from dataclasses import dataclass

from .template_create_response_data_sandboxes import TemplateCreateResponseDataSandboxes

__all__ = ["TemplateCreateResponseData"]

@dataclass
class TemplateCreateResponseData:
    """
    TemplateCreateResponseData dataclass
    
    Args:
        sandboxes (TemplateCreateResponseDataSandboxes)
                                 : 
        tag (str)                : 
    """
    sandboxes: TemplateCreateResponseDataSandboxes
    tag: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "sandboxes": "sandboxes",
            "tag": "tag",
        }
        key_transform_with_dump = {
            "sandboxes": "sandboxes",
            "tag": "tag",
        }
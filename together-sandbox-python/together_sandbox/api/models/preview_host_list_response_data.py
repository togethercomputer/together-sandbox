from dataclasses import dataclass

from .preview_host_list_response_data_preview_hosts import PreviewHostListResponseDataPreviewHosts

__all__ = ["PreviewHostListResponseData"]

@dataclass
class PreviewHostListResponseData:
    """
    PreviewHostListResponseData dataclass
    
    Args:
        preview_hosts (PreviewHostListResponseDataPreviewHosts)
                                 : 
    """
    preview_hosts: PreviewHostListResponseDataPreviewHosts
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "preview_hosts": "preview_hosts",
        }
        key_transform_with_dump = {
            "preview_hosts": "preview_hosts",
        }
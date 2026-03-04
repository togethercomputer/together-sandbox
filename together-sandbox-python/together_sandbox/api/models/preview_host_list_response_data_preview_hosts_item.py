from dataclasses import dataclass

__all__ = ["PreviewHostListResponseDataPreviewHostsItem"]

@dataclass
class PreviewHostListResponseDataPreviewHostsItem:
    """
    PreviewHostListResponseDataPreviewHostsItem dataclass
    
    Args:
        host (str)               : 
        inserted_at (str)        : 
    """
    host: str
    inserted_at: str
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "host": "host",
            "inserted_at": "inserted_at",
        }
        key_transform_with_dump = {
            "host": "host",
            "inserted_at": "inserted_at",
        }
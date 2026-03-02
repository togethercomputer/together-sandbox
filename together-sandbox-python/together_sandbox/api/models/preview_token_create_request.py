from dataclasses import dataclass
from datetime import datetime

__all__ = ["PreviewTokenCreateRequest"]

@dataclass
class PreviewTokenCreateRequest:
    """
    PreviewTokenCreateRequest dataclass
    
    Args:
        expires_at (datetime | None)
                                 : UTC Timestamp until when this token is valid. Omitting
                                   this field will create a token without an expiry.
    """
    expires_at: datetime | None = None  # UTC Timestamp until when this token is valid. Omitting this field will create a token without an expiry.
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "expires_at": "expires_at",
        }
        key_transform_with_dump = {
            "expires_at": "expires_at",
        }
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, List

__all__ = ["TokenCreateRequest"]

@dataclass
class TokenCreateRequest:
    """
    TokenCreateRequest dataclass
    
    Args:
        default_version (date | None)
                                 : API Version to use, formatted as YYYY-MM-DD. Defaults to
                                   the latest version at time of creation.
        description (str | None) : Description of this token, for instance where it will be
                                   used.
        expires_at (datetime | None)
                                 : UTC Timestamp until when this token is valid. Omitting
                                   this field will create a token without an expiry.
        scopes (List[Any] | None): Which scopes to grant this token. The given scopes will
                                   replace the current scopes, revoking any that are no
                                   longer present in the list.
    """
    default_version: date | None = None  # API Version to use, formatted as YYYY-MM-DD. Defaults to the latest version at time of creation.
    description: str | None = None  # Description of this token, for instance where it will be used.
    expires_at: datetime | None = None  # UTC Timestamp until when this token is valid. Omitting this field will create a token without an expiry.
    scopes: List[Any] | None = field(default_factory=list)  # Which scopes to grant this token. The given scopes will replace the current scopes, revoking any that are no longer present in the list.
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "default_version": "default_version",
            "description": "description",
            "expires_at": "expires_at",
            "scopes": "scopes",
        }
        key_transform_with_dump = {
            "default_version": "default_version",
            "description": "description",
            "expires_at": "expires_at",
            "scopes": "scopes",
        }
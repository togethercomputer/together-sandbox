from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, List

__all__ = ["TokenUpdateRequest"]

@dataclass
class TokenUpdateRequest:
    """
    Updateable fields for API Tokens. Omitting a field will not update it; explicitly
    passing null or an empty list will clear the value.
    
    Args:
        default_version (date | None)
                                 : API Version to use, formatted as YYYY-MM-DD
        description (str | None) : Description of this token, for instance where it will be
                                   used.
        expires_at (datetime | None)
                                 : Expiry time of this token. Cannot be set in the past, and
                                   cannot be changed for tokens that have already expired.
                                   Pass null to make this token never expire.
        scopes (List[Any] | None): Which scopes to grant this token. The given scopes will
                                   replace the current scopes, revoking any that are no
                                   longer present in the list.
    """
    default_version: date | None = None  # API Version to use, formatted as YYYY-MM-DD
    description: str | None = None  # Description of this token, for instance where it will be used.
    expires_at: datetime | None = None  # Expiry time of this token. Cannot be set in the past, and cannot be changed for tokens that have already expired. Pass null to make this token never expire.
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
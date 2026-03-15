from __future__ import annotations

from dataclasses import dataclass

from .meta_information_api import MetaInformationApi
from .meta_information_auth import MetaInformationAuth
from .meta_information_rate_limits import MetaInformationRateLimits

__all__ = ["MetaInformation"]

@dataclass
class MetaInformation:
    """
    MetaInformation dataclass
    
    Args:
        api_ (MetaInformationApi): Meta information about the CodeSandbox API (maps from
                                   'api')
        auth (MetaInformationAuth | None)
                                 : Meta information about the current authentication context
        rate_limits (MetaInformationRateLimits | None)
                                 : Current workspace rate limits
    """
    api_: MetaInformationApi  # Meta information about the CodeSandbox API (maps from 'api')
    auth: MetaInformationAuth | None = None  # Meta information about the current authentication context
    rate_limits: MetaInformationRateLimits | None = None  # Current workspace rate limits
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "api": "api_",
            "auth": "auth",
            "rate_limits": "rate_limits",
        }
        key_transform_with_dump = {
            "api_": "api",
            "auth": "auth",
            "rate_limits": "rate_limits",
        }
from dataclasses import dataclass

from .meta_information_rate_limits_concurrent_vms import MetaInformationRateLimitsConcurrentVms
from .meta_information_rate_limits_requests_hourly import MetaInformationRateLimitsRequestsHourly
from .meta_information_rate_limits_sandboxes_hourly import MetaInformationRateLimitsSandboxesHourly

__all__ = ["MetaInformationRateLimits"]

@dataclass
class MetaInformationRateLimits:
    """
    Current workspace rate limits
    
    Args:
        concurrent_vms (MetaInformationRateLimitsConcurrentVms)
                                 : 
        requests_hourly (MetaInformationRateLimitsRequestsHourly)
                                 : 
        sandboxes_hourly (MetaInformationRateLimitsSandboxesHourly)
                                 : 
    """
    concurrent_vms: MetaInformationRateLimitsConcurrentVms
    requests_hourly: MetaInformationRateLimitsRequestsHourly
    sandboxes_hourly: MetaInformationRateLimitsSandboxesHourly
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "concurrent_vms": "concurrent_vms",
            "requests_hourly": "requests_hourly",
            "sandboxes_hourly": "sandboxes_hourly",
        }
        key_transform_with_dump = {
            "concurrent_vms": "concurrent_vms",
            "requests_hourly": "requests_hourly",
            "sandboxes_hourly": "sandboxes_hourly",
        }
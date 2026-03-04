from dataclasses import dataclass

from .vm_update_specs_request_tier import VmUpdateSpecsRequestTier

__all__ = ["VmUpdateSpecsRequest"]

@dataclass
class VmUpdateSpecsRequest:
    """
    VmUpdateSpecsRequest dataclass
    
    Args:
        tier (VmUpdateSpecsRequestTier)
                                 : Determines which specs to update the VM with.  Not all
                                   tiers will be available depending on the workspace
                                   subscription status, and higher tiers incur higher costs.
                                   Please see codesandbox.io/pricing for details on specs
                                   and costs.
    """
    tier: VmUpdateSpecsRequestTier  # Determines which specs to update the VM with.  Not all tiers will be available depending on the workspace subscription status, and higher tiers incur higher costs. Please see codesandbox.io/pricing for details on specs and costs. 
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "tier": "tier",
        }
        key_transform_with_dump = {
            "tier": "tier",
        }
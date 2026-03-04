from dataclasses import dataclass

from .vm_start_request_automatic_wakeup_config import VmStartRequestAutomaticWakeupConfig
from .vm_start_request_tier import VmStartRequestTier

__all__ = ["VmStartRequest2"]

@dataclass
class VmStartRequest2:
    """
    VmStartRequest2 dataclass
    
    Args:
        automatic_wakeup_config (VmStartRequestAutomaticWakeupConfig | None)
                                 : Configuration for when the VM should automatically wake
                                   up from hibernation
        hibernation_timeout_seconds (int | None)
                                 : The time in seconds after which the VM will hibernate due
                                   to inactivity. Must be a positive integer between 1 and
                                   86400 (24 hours). Defaults to 300 seconds (5 minutes) if
                                   not specified.
        ipcountry (str | None)   : This determines in which cluster, closest to the given
                                   country the VM will be started in. The format is
                                   ISO-3166-1 alpha-2. If not set, the VM will be started
                                   closest to the caller of this API. This will only be
                                   applied when a VM is run for the first time, and will
                                   only serve as a hint (e.g. if the template of this
                                   sandbox runs in EU cluster, this sandbox will also run in
                                   the EU cluster).
        tier (VmStartRequestTier | None)
                                 : Determines which specs to start the VM with. If not
                                   specified, the VM will start with the default specs for
                                   the workspace.  You can only specify a VM tier when
                                   starting a VM that is inside your workspace. Specifying a
                                   VM tier for someone else's sandbox will return an error.
                                   Not all tiers will be available depending on the
                                   workspace subscription status, and higher tiers incur
                                   higher costs. Please see codesandbox.io/pricing for
                                   details on specs and costs.
    """
    automatic_wakeup_config: VmStartRequestAutomaticWakeupConfig | None = None  # Configuration for when the VM should automatically wake up from hibernation
    hibernation_timeout_seconds: int | None = None  # The time in seconds after which the VM will hibernate due to inactivity. Must be a positive integer between 1 and 86400 (24 hours). Defaults to 300 seconds (5 minutes) if not specified. 
    ipcountry: str | None = None  # This determines in which cluster, closest to the given country the VM will be started in. The format is ISO-3166-1 alpha-2. If not set, the VM will be started closest to the caller of this API. This will only be applied when a VM is run for the first time, and will only serve as a hint (e.g. if the template of this sandbox runs in EU cluster, this sandbox will also run in the EU cluster).
    tier: VmStartRequestTier | None = None  # Determines which specs to start the VM with. If not specified, the VM will start with the default specs for the workspace.  You can only specify a VM tier when starting a VM that is inside your workspace. Specifying a VM tier for someone else's sandbox will return an error.  Not all tiers will be available depending on the workspace subscription status, and higher tiers incur higher costs. Please see codesandbox.io/pricing for details on specs and costs. 
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "automatic_wakeup_config": "automatic_wakeup_config",
            "hibernation_timeout_seconds": "hibernation_timeout_seconds",
            "ipcountry": "ipcountry",
            "tier": "tier",
        }
        key_transform_with_dump = {
            "automatic_wakeup_config": "automatic_wakeup_config",
            "hibernation_timeout_seconds": "hibernation_timeout_seconds",
            "ipcountry": "ipcountry",
            "tier": "tier",
        }
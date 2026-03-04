from dataclasses import dataclass

from .vm_list_running_v_ms_response_data_vms import VmListRunningVMsResponseDataVms

__all__ = ["VmListRunningVMsResponseData2"]

@dataclass
class VmListRunningVMsResponseData2:
    """
    VmListRunningVMsResponseData2 dataclass
    
    Args:
        concurrent_vm_count (int): 
        concurrent_vm_limit (int): 
        vms (VmListRunningVMsResponseDataVms)
                                 : 
    """
    concurrent_vm_count: int
    concurrent_vm_limit: int
    vms: VmListRunningVMsResponseDataVms
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "concurrent_vm_count": "concurrent_vm_count",
            "concurrent_vm_limit": "concurrent_vm_limit",
            "vms": "vms",
        }
        key_transform_with_dump = {
            "concurrent_vm_count": "concurrent_vm_count",
            "concurrent_vm_limit": "concurrent_vm_limit",
            "vms": "vms",
        }
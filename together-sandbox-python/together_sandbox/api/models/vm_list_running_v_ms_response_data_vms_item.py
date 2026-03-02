from dataclasses import dataclass
from datetime import datetime

from .vm_list_running_v_ms_response_data_vms_item_specs import VmListRunningVMsResponseDataVmsItemSpecs

__all__ = ["VmListRunningVMsResponseDataVmsItem"]

@dataclass
class VmListRunningVMsResponseDataVmsItem:
    """
    VmListRunningVMsResponseDataVmsItem dataclass
    
    Args:
        credit_basis (str | None): 
        id_ (str | None)         : Maps from 'id'
        last_active_at (datetime | None)
                                 : 
        session_started_at (datetime | None)
                                 : 
        specs (VmListRunningVMsResponseDataVmsItemSpecs | None)
                                 : 
    """
    credit_basis: str | None = None
    id_: str | None = None  # Maps from 'id'
    last_active_at: datetime | None = None
    session_started_at: datetime | None = None
    specs: VmListRunningVMsResponseDataVmsItemSpecs | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "credit_basis": "credit_basis",
            "id": "id_",
            "last_active_at": "last_active_at",
            "session_started_at": "session_started_at",
            "specs": "specs",
        }
        key_transform_with_dump = {
            "credit_basis": "credit_basis",
            "id_": "id",
            "last_active_at": "last_active_at",
            "session_started_at": "session_started_at",
            "specs": "specs",
        }
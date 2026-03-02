from dataclasses import dataclass

from .update_exec_request_status import UpdateExecRequestStatus

__all__ = ["UpdateExecRequest"]

@dataclass
class UpdateExecRequest:
    """
    UpdateExecRequest dataclass
    
    Args:
        status (UpdateExecRequestStatus)
                                 : Status to set for the exec (currently only 'running' is
                                   supported)
    """
    status: UpdateExecRequestStatus  # Status to set for the exec (currently only 'running' is supported)
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "status": "status",
        }
        key_transform_with_dump = {
            "status": "status",
        }
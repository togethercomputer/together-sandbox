from dataclasses import dataclass

__all__ = ["VmListRunningVMsResponseDataVmsItemSpecs"]

@dataclass
class VmListRunningVMsResponseDataVmsItemSpecs:
    """
    VmListRunningVMsResponseDataVmsItemSpecs dataclass
    
    Args:
        cpu (int | None)         : 
        memory (int | None)      : 
        storage (int | None)     : 
    """
    cpu: int | None = None
    memory: int | None = None
    storage: int | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "cpu": "cpu",
            "memory": "memory",
            "storage": "storage",
        }
        key_transform_with_dump = {
            "cpu": "cpu",
            "memory": "memory",
            "storage": "storage",
        }
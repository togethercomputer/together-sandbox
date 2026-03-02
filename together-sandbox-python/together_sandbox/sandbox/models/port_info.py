from dataclasses import dataclass

__all__ = ["PortInfo"]

@dataclass
class PortInfo:
    """
    PortInfo dataclass
    
    Args:
        address (str)            : IP address the port is bound to
        port (int)               : Port number
    """
    address: str  # IP address the port is bound to
    port: int  # Port number
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "address": "address",
            "port": "port",
        }
        key_transform_with_dump = {
            "address": "address",
            "port": "port",
        }
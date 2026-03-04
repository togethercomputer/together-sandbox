from dataclasses import dataclass
from typing import List

from .port_info import PortInfo

__all__ = ["PortsListResponse"]

@dataclass
class PortsListResponse:
    """
    PortsListResponse dataclass
    
    Args:
        ports (List[PortInfo])   : List of open ports
    """
    ports: List[PortInfo]  # List of open ports
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "ports": "ports",
        }
        key_transform_with_dump = {
            "ports": "ports",
        }
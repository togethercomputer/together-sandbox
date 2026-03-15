from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SandboxForkRequestStartOptionsAutomaticWakeupConfig"]

@dataclass
class SandboxForkRequestStartOptionsAutomaticWakeupConfig:
    """
    Configuration for when the VM should automatically wake up from hibernation
    
    Args:
        http_ (bool | None)      : Whether the VM should automatically wake up on HTTP
                                   requests (excludes WebSocket requests) (maps from 'http')
        websocket (bool | None)  : Whether the VM should automatically wake up on WebSocket
                                   connections
    """
    http_: bool | None = True  # Whether the VM should automatically wake up on HTTP requests (excludes WebSocket requests) (maps from 'http')
    websocket: bool | None = False  # Whether the VM should automatically wake up on WebSocket connections
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "http": "http_",
            "websocket": "websocket",
        }
        key_transform_with_dump = {
            "http_": "http",
            "websocket": "websocket",
        }
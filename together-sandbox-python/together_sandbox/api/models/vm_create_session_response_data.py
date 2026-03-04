from dataclasses import dataclass
from typing import List

from .vm_create_session_response_data_permissions import VmCreateSessionResponseDataPermissions

__all__ = ["VmCreateSessionResponseData"]

@dataclass
class VmCreateSessionResponseData:
    """
    VmCreateSessionResponseData dataclass
    
    Args:
        capabilities (List[str]) : List of capabilities that Pitcher has
        permissions (VmCreateSessionResponseDataPermissions)
                                 : The permissions of the current session
        pitcher_token (str)      : Token to authenticate with Pitcher (the agent running
                                   inside the VM)
        pitcher_url (str)        : WebSocket URL to connect to Pitcher
        user_workspace_path (str): Path to the user's workspace in the VM
        username (str)           : The Linux username created for this session
    """
    capabilities: List[str]  # List of capabilities that Pitcher has
    permissions: VmCreateSessionResponseDataPermissions  # The permissions of the current session
    pitcher_token: str  # Token to authenticate with Pitcher (the agent running inside the VM)
    pitcher_url: str  # WebSocket URL to connect to Pitcher
    user_workspace_path: str  # Path to the user's workspace in the VM
    username: str  # The Linux username created for this session
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "capabilities": "capabilities",
            "permissions": "permissions",
            "pitcher_token": "pitcher_token",
            "pitcher_url": "pitcher_url",
            "user_workspace_path": "user_workspace_path",
            "username": "username",
        }
        key_transform_with_dump = {
            "capabilities": "capabilities",
            "permissions": "permissions",
            "pitcher_token": "pitcher_token",
            "pitcher_url": "pitcher_url",
            "user_workspace_path": "user_workspace_path",
            "username": "username",
        }
from dataclasses import dataclass

__all__ = ["VmStartResponseData"]

@dataclass
class VmStartResponseData:
    """
    VmStartResponseData dataclass
    
    Args:
        bootup_type (str)        : 
        cluster (str)            : 
        id_ (str)                : Maps from 'id'
        latest_pitcher_version (str)
                                 : 
        pitcher_manager_version (str)
                                 : 
        pitcher_token (str)      : 
        pitcher_url (str)        : 
        pitcher_version (str)    : 
        reconnect_token (str)    : 
        use_pint (bool)          : 
        user_workspace_path (str): 
        vm_agent_type (str)      : 
        workspace_path (str)     : 
        pint_token (str | None)  : 
        pint_url (str | None)    : 
    """
    bootup_type: str
    cluster: str
    id_: str  # Maps from 'id'
    latest_pitcher_version: str
    pitcher_manager_version: str
    pitcher_token: str
    pitcher_url: str
    pitcher_version: str
    reconnect_token: str
    use_pint: bool
    user_workspace_path: str
    vm_agent_type: str
    workspace_path: str
    pint_token: str | None = None
    pint_url: str | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "bootup_type": "bootup_type",
            "cluster": "cluster",
            "id": "id_",
            "latest_pitcher_version": "latest_pitcher_version",
            "pint_token": "pint_token",
            "pint_url": "pint_url",
            "pitcher_manager_version": "pitcher_manager_version",
            "pitcher_token": "pitcher_token",
            "pitcher_url": "pitcher_url",
            "pitcher_version": "pitcher_version",
            "reconnect_token": "reconnect_token",
            "use_pint": "use_pint",
            "user_workspace_path": "user_workspace_path",
            "vm_agent_type": "vm_agent_type",
            "workspace_path": "workspace_path",
        }
        key_transform_with_dump = {
            "bootup_type": "bootup_type",
            "cluster": "cluster",
            "id_": "id",
            "latest_pitcher_version": "latest_pitcher_version",
            "pint_token": "pint_token",
            "pint_url": "pint_url",
            "pitcher_manager_version": "pitcher_manager_version",
            "pitcher_token": "pitcher_token",
            "pitcher_url": "pitcher_url",
            "pitcher_version": "pitcher_version",
            "reconnect_token": "reconnect_token",
            "use_pint": "use_pint",
            "user_workspace_path": "user_workspace_path",
            "vm_agent_type": "vm_agent_type",
            "workspace_path": "workspace_path",
        }
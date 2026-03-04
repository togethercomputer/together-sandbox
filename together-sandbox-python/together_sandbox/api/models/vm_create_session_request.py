from dataclasses import dataclass

from .vm_create_session_request_permission import VmCreateSessionRequestPermission

__all__ = ["VmCreateSessionRequest"]

@dataclass
class VmCreateSessionRequest:
    """
    VmCreateSessionRequest dataclass
    
    Args:
        permission (VmCreateSessionRequestPermission)
                                 : Permission level for the session
        session_id (str)         : Unique identifier for the session
        git_access_token (str | None)
                                 : GitHub token for the session
        git_user_email (str | None)
                                 : Git user email to configure for this session
        git_user_name (str | None): Git user name to configure for this session
    """
    permission: VmCreateSessionRequestPermission  # Permission level for the session
    session_id: str  # Unique identifier for the session
    git_access_token: str | None = None  # GitHub token for the session
    git_user_email: str | None = None  # Git user email to configure for this session
    git_user_name: str | None = None  # Git user name to configure for this session
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "git_access_token": "git_access_token",
            "git_user_email": "git_user_email",
            "git_user_name": "git_user_name",
            "permission": "permission",
            "session_id": "session_id",
        }
        key_transform_with_dump = {
            "git_access_token": "git_access_token",
            "git_user_email": "git_user_email",
            "git_user_name": "git_user_name",
            "permission": "permission",
            "session_id": "session_id",
        }
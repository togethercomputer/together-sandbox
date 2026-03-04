from dataclasses import dataclass

from .file_action_request_action import FileActionRequestAction

__all__ = ["FileActionRequest"]

@dataclass
class FileActionRequest:
    """
    FileActionRequest dataclass
    
    Args:
        action (FileActionRequestAction)
                                 : Type of action to perform on the file
        destination (str)        : Destination path for move operation
        recursive (bool | None)  : Whether to perform the action recursively for directories
    """
    action: FileActionRequestAction  # Type of action to perform on the file
    destination: str  # Destination path for move operation
    recursive: bool | None = None  # Whether to perform the action recursively for directories
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "action": "action",
            "destination": "destination",
            "recursive": "recursive",
        }
        key_transform_with_dump = {
            "action": "action",
            "destination": "destination",
            "recursive": "recursive",
        }
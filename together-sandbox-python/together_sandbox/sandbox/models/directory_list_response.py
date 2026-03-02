from dataclasses import dataclass
from typing import List

from .file_info import FileInfo

__all__ = ["DirectoryListResponse"]

@dataclass
class DirectoryListResponse:
    """
    DirectoryListResponse dataclass
    
    Args:
        files (List[FileInfo])   : List of files and directories
        path (str)               : Directory path
    """
    files: List[FileInfo]  # List of files and directories
    path: str  # Directory path
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "files": "files",
            "path": "path",
        }
        key_transform_with_dump = {
            "files": "files",
            "path": "path",
        }
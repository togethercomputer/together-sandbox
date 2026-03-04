from dataclasses import dataclass

__all__ = ["FileInfo"]

@dataclass
class FileInfo:
    """
    FileInfo dataclass
    
    Args:
        is_dir (bool)            : Whether this entry is a directory (maps from 'isDir')
        mod_time (str)           : Last modification time (maps from 'modTime')
        name (str)               : File or directory name
        path (str)               : Full path to the file or directory
        size (int)               : File size in bytes
    """
    is_dir: bool  # Whether this entry is a directory (maps from 'isDir')
    mod_time: str  # Last modification time (maps from 'modTime')
    name: str  # File or directory name
    path: str  # Full path to the file or directory
    size: int  # File size in bytes
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "isDir": "is_dir",
            "modTime": "mod_time",
            "name": "name",
            "path": "path",
            "size": "size",
        }
        key_transform_with_dump = {
            "is_dir": "isDir",
            "mod_time": "modTime",
            "name": "name",
            "path": "path",
            "size": "size",
        }
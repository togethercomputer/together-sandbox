from dataclasses import dataclass

__all__ = ["SandboxSettings"]

@dataclass
class SandboxSettings:
    """
    SandboxSettings dataclass
    
    Args:
        use_pint (bool | None)   : 
    """
    use_pint: bool | None = None
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "use_pint": "use_pint",
        }
        key_transform_with_dump = {
            "use_pint": "use_pint",
        }
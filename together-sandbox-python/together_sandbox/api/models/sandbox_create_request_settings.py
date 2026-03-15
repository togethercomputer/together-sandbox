from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SandboxCreateRequestSettings"]

@dataclass
class SandboxCreateRequestSettings:
    """
    Sandbox settings.
    
    Args:
        use_pint (bool | None)   : Whether to use Pint for the sandbox.
    """
    use_pint: bool | None = None  # Whether to use Pint for the sandbox.
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "use_pint": "use_pint",
        }
        key_transform_with_dump = {
            "use_pint": "use_pint",
        }
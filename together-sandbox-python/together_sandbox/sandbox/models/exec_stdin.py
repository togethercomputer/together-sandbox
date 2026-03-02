from dataclasses import dataclass

from .type__2 import Type2

__all__ = ["ExecStdin"]

@dataclass
class ExecStdin:
    """
    ExecStdin dataclass
    
    Args:
        input_ (str)             : Data associated with the exec input (maps from 'input')
        type_ (Type2)            : Type of the exec input (maps from 'type')
    """
    input_: str  # Data associated with the exec input (maps from 'input')
    type_: Type2  # Type of the exec input (maps from 'type')
    
    class Meta:
        """Configure field name mapping for JSON conversion."""
        key_transform_with_load = {
            "input": "input_",
            "type": "type_",
        }
        key_transform_with_dump = {
            "input_": "input",
            "type_": "type",
        }
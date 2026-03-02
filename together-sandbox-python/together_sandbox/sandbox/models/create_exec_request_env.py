from collections.abc import ItemsView, KeysView, ValuesView
from dataclasses import dataclass, field
from typing import Any, ClassVar, Iterator

__all__ = ["CreateExecRequestEnv"]

@dataclass
class CreateExecRequestEnv:
    """
    Environment variables to set for the command (key-value pairs)

    This class wraps a dictionary with typed values, providing dict-like access
    while ensuring values are properly deserialized into str instances.

    Example:
        from together_sandbox.core.cattrs_converter import structure_from_dict, unstructure_to_dict

        # Deserialize from API response - values become str instances
        obj = structure_from_dict({"key": {"field": "value"}}, CreateExecRequestEnv)

        # Access returns typed str instance
        item = obj["key"]
        print(item.field)  # "value" - direct attribute access

        # Serialize for API request
        data = unstructure_to_dict(obj)
    """

    _data: dict[str, str] = field(default_factory=dict, repr=False)

    # Runtime type information for cattrs deserialization
    _value_type: ClassVar[str] = "str"

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get value for key, returning default if key not present."""
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> str:
        """Get value for key."""
        return self._data[key]

    def __setitem__(self, key: str, value: str) -> None:
        """Set value for key."""
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._data

    def __bool__(self) -> bool:
        """Return True if wrapper contains any data."""
        return bool(self._data)

    def keys(self) -> KeysView[str]:
        """Return dictionary keys."""
        return self._data.keys()

    def values(self) -> ValuesView[str]:
        """Return dictionary values."""
        return self._data.values()

    def items(self) -> ItemsView[str, str]:
        """Return dictionary items."""
        return self._data.items()

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._data)


# Register cattrs hooks for CreateExecRequestEnv
def _structure_createexecrequestenv(data: dict[str, Any], _: type[CreateExecRequestEnv]) -> CreateExecRequestEnv:
    """Structure hook for cattrs to handle CreateExecRequestEnv deserialization with typed values."""
    if data is None:
        return CreateExecRequestEnv()
    if isinstance(data, CreateExecRequestEnv):
        return data

    # Import converter lazily to avoid circular imports
    from together_sandbox.core.cattrs_converter import converter, _register_structure_hooks_recursively

    # Register hooks for dataclass value types (once, outside loop)
    if hasattr(str, '__dataclass_fields__'):
        _register_structure_hooks_recursively(str)

    # Deserialize each value into str
    # Using converter.structure() for all values - cattrs handles primitives, datetime, bytes, etc.
    structured_data: dict[str, str] = {}
    for key, value in data.items():
        structured_data[key] = converter.structure(value, str)

    return CreateExecRequestEnv(_data=structured_data)


def _unstructure_createexecrequestenv(instance: CreateExecRequestEnv) -> dict[str, Any]:
    """Unstructure hook for cattrs to handle CreateExecRequestEnv serialization."""
    from together_sandbox.core.cattrs_converter import converter

    # Unstructure each value
    return {
        key: converter.unstructure(value)
        for key, value in instance._data.items()
    }


# Register hooks with cattrs converter at module import time
from together_sandbox.core.cattrs_converter import converter
converter.register_structure_hook(CreateExecRequestEnv, _structure_createexecrequestenv)
converter.register_unstructure_hook(CreateExecRequestEnv, _unstructure_createexecrequestenv)

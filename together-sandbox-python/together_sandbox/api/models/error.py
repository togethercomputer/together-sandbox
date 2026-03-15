from __future__ import annotations

from typing import Any, Dict, TypeAlias, Union

__all__ = ['Error']

Error: TypeAlias = Union[str, dict[str, Any]]
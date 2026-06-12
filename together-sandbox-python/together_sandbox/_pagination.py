from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """One page of a cursor-paginated list response.

    Pass :attr:`next_cursor` back as the ``cursor`` argument to fetch the
    following page; it is ``None`` on the last page.
    """

    data: list[T]
    """The items in this page."""

    next_cursor: str | None
    """Cursor to fetch the next page; ``None`` when there are no more items."""

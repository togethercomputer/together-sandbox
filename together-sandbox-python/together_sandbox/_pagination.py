from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class Page(Generic[T]):
    """A single page of a cursor-paginated result.

    A :class:`Page` holds one page of items (:attr:`data` + :attr:`next_cursor`)
    and is itself async-iterable across *all* remaining pages. The common case —
    iterate every item — needs no cursor handling::

        async for snapshot in await sdk.snapshots.list():
            print(snapshot.id)

    Page-by-page control is available when the cursor matters::

        page = await sdk.snapshots.list(limit=50)
        while page.has_next_page():
            print(page.data, page.next_cursor)
            page = await page.get_next_page()
    """

    def __init__(
        self,
        data: list[T],
        next_cursor: str | None,
        fetch: Callable[[str | None], Awaitable[Page[T]]],
    ) -> None:
        #: Items in this page.
        self.data = data
        #: Cursor for the next page, or ``None`` when this is the last page.
        self.next_cursor = next_cursor
        #: Fetches a page starting at the given cursor (``None`` ⇒ first page).
        self._fetch = fetch

    def has_next_page(self) -> bool:
        """Whether a further page exists."""
        return self.next_cursor is not None

    async def get_next_page(self) -> Page[T]:
        """Fetch the next page.

        Raises:
            RuntimeError: If called when :meth:`has_next_page` is ``False``.
        """
        if self.next_cursor is None:
            raise RuntimeError(
                "No next page: get_next_page() called on the last page. "
                "Guard with has_next_page() before calling."
            )
        return await self._fetch(self.next_cursor)

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate every item across all pages, fetching pages on demand."""
        page: Page[T] = self
        while True:
            for item in page.data:
                yield item
            if not page.has_next_page():
                return
            page = await page.get_next_page()

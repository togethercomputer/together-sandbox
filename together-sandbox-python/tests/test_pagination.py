"""Unit tests for the cursor-pagination Page helper."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from together_sandbox._pagination import Page


def make_pages(pages: list[tuple[list[int], str | None]]) -> tuple[AsyncMock, Page[int]]:
    """Build a Page chain backed by a fake fetcher serving fixed pages by cursor.

    Each entry is ``(data, next_cursor)``; the cursor is the string index of the
    next page. Returns the fetch mock (to assert lazy fetching) and the first
    page is built via ``fetch(None)`` by the caller.
    """

    async def _fetch(cursor: str | None) -> Page[int]:
        index = 0 if cursor is None else int(cursor)
        data, next_cursor = pages[index]
        return Page(data, next_cursor, fetch)

    fetch = AsyncMock(side_effect=_fetch)
    return fetch, None  # type: ignore[return-value]


class TestPage:
    async def test_exposes_data_and_next_cursor(self):
        fetch, _ = make_pages([([1, 2], "1")])
        page = await fetch(None)
        assert page.data == [1, 2]
        assert page.next_cursor == "1"
        assert page.has_next_page() is True

    async def test_last_page_has_no_next(self):
        fetch, _ = make_pages([([1], None)])
        page = await fetch(None)
        assert page.has_next_page() is False
        with pytest.raises(RuntimeError, match="No next page"):
            await page.get_next_page()

    async def test_get_next_page_fetches_at_cursor(self):
        fetch, _ = make_pages([([1], "1"), ([2], None)])
        page1 = await fetch(None)
        page2 = await page1.get_next_page()
        assert page2.data == [2]
        assert page2.has_next_page() is False

    async def test_async_iterates_all_items_across_pages(self):
        fetch, _ = make_pages([([1, 2], "1"), ([3], "2"), ([4, 5], None)])
        page = await fetch(None)
        collected = [item async for item in page]
        assert collected == [1, 2, 3, 4, 5]

    async def test_fetches_subsequent_pages_lazily(self):
        fetch, _ = make_pages([([1], "1"), ([2], None)])
        page = await fetch(None)
        assert fetch.call_count == 1  # only the first page so far

        iterator = page.__aiter__()
        await iterator.__anext__()  # yields 1 from in-hand page — no fetch yet
        assert fetch.call_count == 1

        await iterator.__anext__()  # exhausts page 1 → fetches page 2
        assert fetch.call_count == 2

    async def test_single_page_needs_no_extra_fetch(self):
        fetch, _ = make_pages([([1, 2], None)])
        page = await fetch(None)
        collected = [item async for item in page]
        assert collected == [1, 2]
        assert fetch.call_count == 1

"""E2E tests for cursor pagination on the list endpoints.

Covers ``sdk.snapshots.list()`` and ``sdk.sandboxes.list()`` — the ``Page``
envelope, ``limit`` handling, cursor advancement via ``get_next_page()``, and
async iteration across pages.

These tests are read-only and **bounded**: the test account may hold thousands
of items, so they never traverse the full result set. Pagination is keyed on
item ID (the cursor), so there is no recency ordering to exploit — instead the
tests verify the pagination *mechanics* over at most a handful of pages, which
holds regardless of how many items the account has (including zero).
"""

from __future__ import annotations

import os
from typing import Any

import pytest

from together_sandbox import Page, TogetherSandbox
from together_sandbox.api.models.sandbox import Sandbox
from together_sandbox.api.models.snapshot import Snapshot

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("TOGETHER_API_KEY"),
        reason="TOGETHER_API_KEY not set",
    ),
]

# Bound traversal — the test account may hold thousands of items, so we walk
# only enough pages to prove the cursor mechanics, never the whole set.
_MAX_PAGES = 5
_LIMIT = 2


async def _walk(
    first: Page[Any], max_pages: int = _MAX_PAGES
) -> tuple[list[str], list[str | None]]:
    """Walk up to ``max_pages`` pages from ``first``.

    Returns ``(item_ids, cursors_used_to_advance)`` — the latter holds the
    ``next_cursor`` value consumed at each ``get_next_page()`` step.
    """
    ids: list[str] = []
    used_cursors: list[str | None] = []
    page = first
    for _ in range(max_pages):
        ids.extend(item.id for item in page.data)
        if not page.has_next_page():
            break
        used_cursors.append(page.next_cursor)
        page = await page.get_next_page()
    return ids, used_cursors


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["snapshots", "sandboxes"])
class TestListPagination:
    """Pagination contract, exercised identically for both list endpoints."""

    @staticmethod
    def _lister(sdk: TogetherSandbox, kind: str) -> tuple[Any, type]:
        if kind == "snapshots":
            return sdk.snapshots.list, Snapshot
        return sdk.sandboxes.list, Sandbox

    async def test_list_returns_typed_page(
        self, sdk: TogetherSandbox, kind: str
    ) -> None:
        list_fn, item_type = self._lister(sdk, kind)
        page = await list_fn()
        assert isinstance(page, Page)
        assert isinstance(page.data, list)
        assert page.next_cursor is None or isinstance(page.next_cursor, str)
        for item in page.data:
            assert isinstance(item, item_type)

    async def test_limit_is_honored(self, sdk: TogetherSandbox, kind: str) -> None:
        list_fn, _ = self._lister(sdk, kind)
        page = await list_fn(limit=_LIMIT)
        assert len(page.data) <= _LIMIT
        if page.has_next_page():
            # A further page exists, so this one must be full and carry a cursor.
            assert len(page.data) == _LIMIT
            assert isinstance(page.next_cursor, str)

    async def test_cursor_advances_without_duplicates(
        self, sdk: TogetherSandbox, kind: str
    ) -> None:
        list_fn, _ = self._lister(sdk, kind)
        first = await list_fn(limit=_LIMIT)
        ids, used_cursors = await _walk(first)
        # No item appears on more than one page within the walked window.
        assert len(ids) == len(set(ids))
        # Every advancing cursor is a real, distinct value — the cursor moves
        # forward rather than looping on the same position.
        assert all(c is not None for c in used_cursors)
        assert len(set(used_cursors)) == len(used_cursors)

    async def test_async_iteration_crosses_page_boundary(
        self, sdk: TogetherSandbox, kind: str
    ) -> None:
        list_fn, item_type = self._lister(sdk, kind)
        if not (await list_fn(limit=_LIMIT)).has_next_page():
            pytest.skip(f"account has <= {_LIMIT} {kind}; no second page to fetch")

        # Iterate, stopping as soon as we've collected more than one page worth —
        # proving the iterator auto-fetched past the first page. Bounded so we
        # never walk the whole (possibly huge) account.
        seen: list[str] = []
        async for item in await list_fn(limit=_LIMIT):
            assert isinstance(item, item_type)
            seen.append(item.id)
            if len(seen) > _LIMIT * 2:
                break

        assert len(seen) > _LIMIT  # crossed at least one page boundary
        assert len(seen) == len(set(seen))  # no duplicates across pages

"""Tests for the cursor-paginated list facades.

The facade just unwraps the generated response into a ``Page`` and forwards
pagination params, so ``parsed`` is faked with a ``SimpleNamespace`` carrying
``data`` / ``next_cursor`` — no need to build full model instances.
"""

from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from together_sandbox import Page
from together_sandbox._sandboxes import SandboxesNamespace
from together_sandbox._snapshots import SnapshotsNamespace
from together_sandbox.api.types import UNSET, Response


def _page_response(items, next_cursor):
    return Response(
        status_code=HTTPStatus.OK,
        content=b"",
        headers={},
        parsed=SimpleNamespace(data=items, next_cursor=next_cursor),
    )


class TestSnapshotsList:
    async def test_returns_page_and_forwards_params(self):
        item = object()
        api = AsyncMock(return_value=_page_response([item], "next-token"))
        with patch("together_sandbox._snapshots.list_snapshots_api", api):
            ns = SnapshotsNamespace(MagicMock(), "https://x", api_key="key")
            page = await ns.list(limit=5, cursor="c", project_id="p")

        assert isinstance(page, Page)
        assert page.data == [item]
        assert page.next_cursor == "next-token"
        _, kwargs = api.call_args
        assert kwargs["limit"] == 5
        assert kwargs["cursor"] == "c"
        assert kwargs["project_id"] == "p"

    async def test_omitted_params_are_unset(self):
        api = AsyncMock(return_value=_page_response([], None))
        with patch("together_sandbox._snapshots.list_snapshots_api", api):
            ns = SnapshotsNamespace(MagicMock(), "https://x", api_key="key")
            page = await ns.list()

        assert page.data == []
        assert page.next_cursor is None
        _, kwargs = api.call_args
        assert kwargs["limit"] is UNSET
        assert kwargs["cursor"] is UNSET
        assert kwargs["project_id"] is UNSET


class TestSandboxesList:
    async def test_returns_page_and_forwards_params(self):
        item = object()
        api = AsyncMock(return_value=_page_response([item], None))
        with patch("together_sandbox._sandboxes.list_sandboxes_api", api):
            ns = SandboxesNamespace(MagicMock())
            page = await ns.list(limit=10)

        assert isinstance(page, Page)
        assert page.data == [item]
        assert page.next_cursor is None
        _, kwargs = api.call_args
        assert kwargs["limit"] == 10
        assert kwargs["cursor"] is UNSET
        assert kwargs["project_id"] is UNSET


class TestSandboxesGet:
    async def test_returns_record_and_forwards_id(self):
        record = object()
        resp = Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=record
        )
        api = AsyncMock(return_value=resp)
        with patch("together_sandbox._sandboxes.get_sandbox_api", api):
            ns = SandboxesNamespace(MagicMock())
            result = await ns.get("sb_1")

        assert result is record
        args, kwargs = api.call_args
        # id is passed positionally as the first argument
        assert args[0] == "sb_1"

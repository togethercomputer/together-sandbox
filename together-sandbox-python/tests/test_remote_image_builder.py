"""Tests for the fields the remote image builder puts on the wire.

The builder POSTs a multipart form to the image-builder service; these tests
assert the form fields rather than mocking at a higher level, since the field
names are the actual contract with that service. Log streaming is stubbed out —
it needs a live build and is not what these cover.
"""

import tarfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from together_sandbox._remote_image_builder import RemoteImageBuilderClient


@pytest.fixture
def context_dir(tmp_path: Path) -> Path:
    (tmp_path / "Dockerfile").write_text("FROM alpine\n")
    return tmp_path


async def submit(context_dir: Path, **kwargs) -> dict:
    """Run a build with the network stubbed; return the captured POST kwargs."""
    calls: list = []

    async def post(url, **kw):
        assert url == "https://ib.test/builds"
        calls.append(kw)
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json = MagicMock(return_value={"build_id": "b1"})
        return response

    http = MagicMock()
    http.post = post
    http.__aenter__ = AsyncMock(return_value=http)
    http.__aexit__ = AsyncMock(return_value=False)

    client = RemoteImageBuilderClient(api_url="https://ib.test", token="tok")

    with (
        patch("httpx.AsyncClient", return_value=http),
        patch.object(
            RemoteImageBuilderClient,
            "_stream_until_done",
            AsyncMock(return_value="registry/ns/app:v1"),
        ),
    ):
        result = await client.build(
            context_dir=context_dir, image_name="app:v1", **kwargs
        )

    assert result == "registry/ns/app:v1"
    assert len(calls) == 1, f"expected exactly one POST, got {len(calls)}"
    return calls[0]


class TestCacheKey:
    async def test_sent_when_given(self, context_dir: Path):
        call = await submit(context_dir, cache_key="envs/python")
        assert call["data"]["cache_key"] == "envs/python"

    async def test_omitted_when_absent(self, context_dir: Path):
        call = await submit(context_dir)
        # Absent rather than empty: the server defaults an omitted cache_key to
        # the image name without its tag.
        assert "cache_key" not in call["data"]

    async def test_omitted_when_empty(self, context_dir: Path):
        call = await submit(context_dir, cache_key="")
        assert "cache_key" not in call["data"]


class TestOtherFields:
    async def test_unchanged_by_cache_key(self, context_dir: Path):
        call = await submit(context_dir, cache_key="k")
        data = call["data"]
        assert data["image_name"] == "app:v1"
        assert data["dockerfile"] == "Dockerfile"
        assert data["build_args"] == "{}"
        assert data["nydus_convert"] == "true"

    async def test_context_is_a_gzipped_tar(self, context_dir: Path):
        call = await submit(context_dir)
        name, fileobj, content_type = call["files"]["context"]
        assert name == "context.tar.gz"
        assert content_type == "application/gzip"
        fileobj.seek(0)
        with tarfile.open(fileobj=fileobj, mode="r:gz") as tar:
            assert "./Dockerfile" in tar.getnames()

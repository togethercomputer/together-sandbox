"""Unit tests for base URL, builder URL and image-optimization selection."""

from __future__ import annotations

import pytest
from together_sandbox._configuration import (
    get_builder_url,
    get_inferred_base_url,
    is_erofs_enabled,
    is_nydus_enabled,
)


def test_default_base_url_is_v2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
    assert get_inferred_base_url() == "https://api.v2.us.codesandbox.io"


def test_base_url_env_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_BASE_URL", "https://api.bartender.codesandbox.io")
    assert get_inferred_base_url() == "https://api.bartender.codesandbox.io"


@pytest.mark.parametrize(
    ("api", "builder"),
    [
        ("https://api.v2.us.codesandbox.io", "https://builder.codesandbox.io"),
        ("https://api.bartender.codesandbox.io", "https://builder.codesandbox.io"),
        ("https://api.codesandbox.dev", "https://builder.codesandbox.dev"),
        ("http://localhost:4000", "http://localhost:4000"),
    ],
)
def test_builder_url(api: str, builder: str) -> None:
    assert get_builder_url(api) == builder


@pytest.mark.parametrize(
    ("api", "erofs", "nydus"),
    [
        ("https://api.v2.us.codesandbox.io", True, False),
        ("https://api.bartender-v2.codesandbox.stream", True, False),
        ("https://api.bartender.codesandbox.io", False, True),
        ("https://api.codesandbox.dev", False, False),
    ],
)
def test_optimization_by_host(
    monkeypatch: pytest.MonkeyPatch, api: str, erofs: bool, nydus: bool
) -> None:
    monkeypatch.delenv("TOGETHER_EROFS_ENABLED", raising=False)
    monkeypatch.delenv("TOGETHER_NYDUS_ENABLED", raising=False)
    assert is_erofs_enabled(api) is erofs
    assert is_nydus_enabled(api) is nydus

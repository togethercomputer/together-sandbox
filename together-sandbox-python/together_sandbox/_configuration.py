from __future__ import annotations

import os
from urllib.parse import urlparse

DEFAULT_BASE_URL = "https://api.bartender.codesandbox.stream"


def get_inferred_base_url() -> str:
    return os.environ.get("TOGETHER_BASE_URL") or DEFAULT_BASE_URL


def is_local_environment(base_url: str) -> bool:
    return urlparse(base_url).hostname == "api.codesandbox.dev"

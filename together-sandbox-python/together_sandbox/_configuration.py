from __future__ import annotations

import os
import platform
from urllib.parse import urlparse, urlunparse

DEFAULT_BASE_URL = "https://api.bartender.codesandbox.io"


def get_inferred_base_url() -> str:
    return os.environ.get("TOGETHER_BASE_URL") or DEFAULT_BASE_URL


def get_builder_url(base_url: str) -> str:
    """
    Derive the image-builder service URL from the management API base URL: the
    "builder" subdomain of the same registrable domain, so any API hostname on a
    given domain resolves to that domain's single builder host.

        https://api.bartender.codesandbox.io   -> https://builder.codesandbox.io
        https://api2.bartender.codesandbox.dev -> https://builder.codesandbox.dev
        https://api.codesandbox.dev            -> https://builder.codesandbox.dev

    Hosts with no domain to attach a subdomain to ("localhost", IP literals) are
    returned unchanged, so local setups keep talking to what they configured.
    Mirrors the TypeScript SDK's `getBuilderUrl`.
    """
    parsed = urlparse(base_url)
    host = parsed.hostname or ""
    labels = host.split(".")

    # urlparse strips the brackets from IPv6 literals, leaving the colons.
    is_ip_literal = ":" in host or all(label.isdigit() for label in labels)
    if is_ip_literal or len(labels) < 2:
        return base_url

    netloc = "builder." + ".".join(labels[-2:])
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return urlunparse(parsed._replace(netloc=netloc)).rstrip("/")


def is_local_environment(base_url: str) -> bool:
    """
    True when the API base URL points at the local "codesandbox.dev" environment
    (any hostname on that domain, e.g. "api.codesandbox.dev" or
    "api2.bartender.codesandbox.dev"), where the services — including the image
    builder — run on this machine.
    """
    host = urlparse(base_url).hostname or ""

    return host == "codesandbox.dev" or host.endswith(".codesandbox.dev")


def get_host_architecture() -> str:
    """Architecture of the machine running the SDK, as "amd64" or "arm64"."""
    return "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "amd64"

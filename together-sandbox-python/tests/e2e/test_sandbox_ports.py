"""E2E tests for sandbox port operations.

They reach a port through the URL ``sandbox.ports.get_url`` builds from the
agent URL, the way any client would, so they check the URL actually routes to
the port inside the sandbox, not just that it has the expected shape.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from together_sandbox import Sandbox

PORT = 8080


async def start_server(sandbox: Sandbox, port: int, body: str) -> None:
    """Serve a fixed 200 response with ``body`` on ``port`` with busybox nc."""
    script = (
        "while true; do "
        "printf 'HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n"
        f"Content-Length: {len(body)}\\r\\nConnection: close\\r\\n\\r\\n{body}' "
        f"| nc -l -p {port}; "
        "done"
    )
    await sandbox.execs.create(command="sh", args=["-c", script])


async def wait_for_response(
    client: httpx.AsyncClient, url: str, timeout: float = 30.0
) -> httpx.Response:
    """Wait for ``url`` to answer 200 through the proxy and return the response."""
    deadline = asyncio.get_event_loop().time() + timeout
    last: object = None
    while asyncio.get_event_loop().time() < deadline:
        try:
            response = await client.get(url, timeout=15.0)
            if response.status_code == 200:
                return response
            last = response.status_code
        except httpx.HTTPError as e:
            last = e
        await asyncio.sleep(0.5)
    raise TimeoutError(f"{url} did not serve within {timeout}s (last: {last})")


@pytest.mark.e2e
@pytest.mark.asyncio
class TestSandboxPorts:
    """E2E tests for port URLs."""

    async def test_get_url_reaches_the_port(self, sandbox: Sandbox):
        """The URL from get_url serves what a server on that port responds."""
        await start_server(sandbox, PORT, "ok")

        url = sandbox.ports.get_url(PORT)
        assert url.startswith("https://"), url

        async with httpx.AsyncClient() as client:
            response = await wait_for_response(client, url)
        assert response.text == "ok"

    async def test_get_url_distinguishes_ports(self, sandbox: Sandbox):
        """Each port's URL reaches that port's server, not another one's."""
        await start_server(sandbox, PORT, "first")
        await start_server(sandbox, PORT + 1, "second")

        first_url = sandbox.ports.get_url(PORT)
        second_url = sandbox.ports.get_url(PORT + 1)
        assert first_url != second_url

        async with httpx.AsyncClient() as client:
            first = await wait_for_response(client, first_url)
            second = await wait_for_response(client, second_url)
        assert first.text == "first"
        assert second.text == "second"

    async def test_get_url_rejects_an_invalid_port(self, sandbox: Sandbox):
        with pytest.raises(RuntimeError, match="Invalid port"):
            sandbox.ports.get_url(0)

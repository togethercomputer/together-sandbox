"""E2E tests for the experimental network policy (inbound allowlist).

They create real sandboxes with a policy and reach their ports through the
public preview URL (``https://<sandbox-id>-<port>.<sandbox domain>``), the way
any client would, so they cover the whole path: the SDK, the API, the sandbox
and the proxy in front of its ports.
"""

from __future__ import annotations

import asyncio
import re

import httpx
import pytest

from together_sandbox import Sandbox, TogetherSandbox
from together_sandbox.errors import HttpError

from .helpers import get_snapshot_id

# The agent's port, which the agent URL points at.
AGENT_PORT = 57468

OPEN_PORT = 8080  # allowed to everyone
TOKEN_PORT = 8081  # allowed with the agent token
OTHER_NETWORK_PORT = 8082  # allowed only from a network the test never runs in
UNLISTED_PORT = 8083  # not in the allowlist

# TEST-NET-1 (RFC 5737): documentation-only, never a real client's address.
OTHER_NETWORK = "192.0.2.0/24"

POLICY = {
    "network_policy": {
        "inbound_allowlist": [
            {"ports": [str(OPEN_PORT)]},
            {"ports": [str(TOKEN_PORT)], "requires_token": True},
            {"ports": [str(OTHER_NETWORK_PORT)], "from": [OTHER_NETWORK]},
        ]
    }
}


def port_url(sandbox: Sandbox, port: int) -> str:
    """The preview URL of a sandbox port, derived from its agent URL."""
    agent_url = sandbox.vm_info.agent.url
    assert agent_url, "a running sandbox has an agent URL"
    url, n = re.subn(rf"-{AGENT_PORT}\.", f"-{port}.", agent_url, count=1)
    assert n == 1, f"unexpected agent URL {agent_url!r}"
    return url.rstrip("/") + "/"


async def start_servers(sandbox: Sandbox, ports: list[int]) -> None:
    """Serve a fixed 200 response on each port with busybox nc, appending each
    request it receives (its headers) to /tmp/request-<port>.txt."""
    for port in ports:
        script = (
            "while true; do "
            "printf 'HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n"
            "Content-Length: 2\\r\\nConnection: close\\r\\n\\r\\nok' "
            f"| nc -l -p {port} >> /tmp/request-{port}.txt; "
            "done"
        )
        await sandbox.execs.create(command="sh", args=["-c", script])


async def get(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    return await client.get(url, timeout=15.0, **kwargs)


async def wait_until_serving(
    client: httpx.AsyncClient, url: str, timeout: float = 30.0
) -> None:
    """Wait for a port's server to answer through the proxy."""
    deadline = asyncio.get_event_loop().time() + timeout
    last: object = None
    while asyncio.get_event_loop().time() < deadline:
        try:
            response = await get(client, url)
            if response.status_code == 200:
                return
            last = response.status_code
        except httpx.HTTPError as e:
            last = e
        await asyncio.sleep(0.5)
    raise TimeoutError(f"{url} did not serve within {timeout}s (last: {last})")


@pytest.mark.asyncio
class TestNetworkPolicy:
    """E2E tests for the inbound allowlist."""

    async def test_inbound_allowlist(self, sdk: TogetherSandbox):
        sandbox = await sdk.sandboxes.create(
            snapshot_id=get_snapshot_id(), experimental=POLICY
        )
        try:
            # The policy is returned, with the defaults filled in.
            policy = sandbox.vm_info.experimental.network_policy
            rules = [rule.to_dict() for rule in policy.inbound_allowlist]
            assert rules == [
                {"ports": [str(OPEN_PORT)], "from": ["*"], "requires_token": False},
                {"ports": [str(TOKEN_PORT)], "from": ["*"], "requires_token": True},
                {
                    "ports": [str(OTHER_NETWORK_PORT)],
                    "from": [OTHER_NETWORK],
                    "requires_token": False,
                },
            ]

            # The agent's port is never filtered: the SDK keeps working, though no
            # rule lists it.
            await sandbox.files.create("/tmp/agent-reachable", "yes")
            assert await sandbox.files.read("/tmp/agent-reachable") == "yes"

            await start_servers(
                sandbox, [OPEN_PORT, TOKEN_PORT, OTHER_NETWORK_PORT, UNLISTED_PORT]
            )

            token = sandbox.vm_info.agent.token
            assert token

            async with httpx.AsyncClient() as client:
                await wait_until_serving(client, port_url(sandbox, OPEN_PORT))

                # A port open to everyone.
                response = await get(client, port_url(sandbox, OPEN_PORT))
                assert response.status_code == 200
                assert response.text == "ok"

                # A port that requires the token.
                response = await get(client, port_url(sandbox, TOKEN_PORT))
                assert response.status_code == 403, response.text

                response = await get(
                    client,
                    port_url(sandbox, TOKEN_PORT),
                    headers={"X-Sandbox-Token": "not-the-token"},
                )
                assert response.status_code == 403, response.text

                response = await get(
                    client,
                    port_url(sandbox, TOKEN_PORT),
                    headers={"X-Sandbox-Token": token},
                )
                assert response.status_code == 200, response.text
                assert response.text == "ok"

                # The token never reaches the sandbox.
                request = await sandbox.files.read(f"/tmp/request-{TOKEN_PORT}.txt")
                assert request.startswith("GET / HTTP/1.1"), request
                assert "x-sandbox-token" not in request.lower(), request

                # A port allowed only from another network.
                response = await get(client, port_url(sandbox, OTHER_NETWORK_PORT))
                assert response.status_code == 403, response.text

                # A port no rule lists, even with the token.
                response = await get(
                    client,
                    port_url(sandbox, UNLISTED_PORT),
                    headers={"X-Sandbox-Token": token},
                )
                assert response.status_code == 403, response.text
        finally:
            await asyncio.wait_for(sdk.sandboxes.terminate(sandbox.id), timeout=30.0)

    async def test_no_policy_allows_every_port(
        self, sdk: TogetherSandbox, sandbox: Sandbox
    ):
        assert sandbox.vm_info.experimental.network_policy is None

        await start_servers(sandbox, [UNLISTED_PORT])
        async with httpx.AsyncClient() as client:
            await wait_until_serving(client, port_url(sandbox, UNLISTED_PORT))

    async def test_invalid_policy_is_rejected(self, sdk: TogetherSandbox):
        with pytest.raises(HttpError) as error:
            await sdk.sandboxes.create(
                snapshot_id=get_snapshot_id(),
                experimental={"network_policy": {"inbound_allowlist": [{"ports": []}]}},
            )
        assert error.value.status == 400

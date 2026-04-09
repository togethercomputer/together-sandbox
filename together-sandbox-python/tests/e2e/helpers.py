"""E2E test helpers for Together Sandbox Python SDK."""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator, Awaitable, Callable, TypeVar

import pytest

from together_sandbox.facade import Sandbox, TogetherSandbox

T = TypeVar("T")


def get_api_key() -> str:
    """Get API key from environment variable."""
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        pytest.skip("TOGETHER_API_KEY environment variable not set")
    return api_key


def get_template_id() -> str | None:
    """Get template ID from environment variable (optional)."""
    return os.environ.get("TOGETHER_TEMPLATE_ID")


def get_base_url() -> str | None:
    """Get base URL from environment variable (optional)."""
    return os.environ.get("TOGETHER_BASE_URL")


@pytest.fixture
async def sdk() -> AsyncGenerator[TogetherSandbox, None]:
    """
    Pytest fixture that provides a configured TogetherSandbox SDK instance.

    Yields:
        TogetherSandbox instance configured with API key from environment
    """
    api_key = get_api_key()
    base_url = get_base_url()

    # Initialize SDK with optional base_url
    if base_url:
        client = TogetherSandbox(api_key=api_key, base_url=base_url)
    else:
        client = TogetherSandbox(api_key=api_key)

    yield client

    # Cleanup if needed (SDK doesn't require explicit cleanup)


@pytest.fixture
async def sandbox(sdk: TogetherSandbox) -> AsyncGenerator[Sandbox, None]:
    """
    Pytest fixture that starts a sandbox instance and cleans it up after tests.

    Args:
        sdk: TogetherSandbox SDK instance from sdk fixture

    Yields:
        Sandbox instance that will be shut down after the test completes
    """
    template_id = get_template_id()

    if not template_id:
        pytest.skip("TOGETHER_TEMPLATE_ID environment variable not set")

    # Start sandbox with the template ID
    sb = await sdk.sandboxes.start(template_id)

    try:
        yield sb
    finally:
        # Cleanup: shutdown sandbox with timeout protection
        try:
            await asyncio.wait_for(
                sdk.sandboxes.shutdown(sb.id),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            print(f"Warning: Timeout while shutting down sandbox {sb.id}")
        except Exception as e:
            print(f"Warning: Error shutting down sandbox {sb.id}: {e}")


async def retry_until(
    fn: Callable[[], Awaitable[T]],
    predicate: Callable[[T], bool],
    timeout: float = 5.0,
    interval: float = 0.1,
) -> T:
    """
    Retry a function until a predicate is satisfied or timeout is reached.

    Args:
        fn: Async function to call repeatedly
        predicate: Function that returns True when the result is satisfactory
        timeout: Maximum time to retry in seconds (default: 5.0)
        interval: Time between retries in seconds (default: 0.1)

    Returns:
        The result from fn when predicate returns True

    Raises:
        TimeoutError: If predicate is never satisfied within timeout period
    """
    start_time = asyncio.get_event_loop().time()

    while True:
        result = await fn()
        if predicate(result):
            return result

        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout:
            raise TimeoutError(
                f"Condition not met within {timeout}s. Last result: {result}"
            )

        await asyncio.sleep(interval)

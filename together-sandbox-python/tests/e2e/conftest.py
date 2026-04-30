"""Pytest configuration for e2e tests."""

# Import fixtures to make them available to all test files
from .helpers import sandbox, sdk  # noqa: F401


def pytest_collection_modifyitems(items):
    for item in items:
        if item.fspath and "tests/e2e" in str(item.fspath):
            item.add_marker("e2e")

"""Pytest configuration for e2e tests."""

# Import fixtures to make them available to all test files
from .helpers import sandbox, sdk  # noqa: F401

# Configure pytest plugins
pytest_plugins = []

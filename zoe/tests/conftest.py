"""pytest configuration for ZOE tests."""

import pytest
import asyncio


def pytest_collection_modifyitems(config, items):
    """Marca tests async automáticamente."""
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


def pytest_configure(config):
    """Configura markers."""
    config.addinivalue_line("markers", "asyncio: mark test as async")

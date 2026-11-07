"""Fixtures shared by the reference tests.

The suite runs under ``--import-mode=importlib``, so a test module cannot import this file by
name: values reach the tests as fixtures. The one fixture is a real gateway, because a double is
always built inside the test that is about it.
"""

import pytest
from mocking_reference.carriers import FastlineGateway


@pytest.fixture
def fastline() -> FastlineGateway:
    return FastlineGateway()

"""Agent test configuration"""

import pytest


# Override the reset_databases fixture from parent conftest
@pytest.fixture
def reset_databases():
    """No-op override of parent reset_databases fixture for agent tests"""
    yield  # Agent tests don't need database setup


@pytest.fixture(scope="session", autouse=True)
def setup_agent_tests():
    """Setup for agent tests without database dependencies"""
    # No database setup needed for agent tests
    yield

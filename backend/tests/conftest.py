"""
Pytest configuration
"""
import pytest


@pytest.fixture(autouse=True)
def reset_databases():
    """Reset in-memory databases before each test"""
    from app.api import auth, projects
    
    # Clear in-memory stores
    auth.users_db.clear()
    projects.projects_db.clear()
    
    yield
    
    # Cleanup after test
    auth.users_db.clear()
    projects.projects_db.clear()

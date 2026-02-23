"""
Role-Based Access Control (RBAC).

Defines roles, permissions, and FastAPI dependency helpers for enforcing
access control on endpoints.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Set

from fastapi import Depends, HTTPException, status

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


# Permission constants
class Permission(str, Enum):
    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_START = "project:start"
    # Scan permissions
    SCAN_READ = "scan:read"
    SCAN_WRITE = "scan:write"
    # Graph permissions
    GRAPH_READ = "graph:read"
    # Admin permissions
    USER_MANAGE = "user:manage"
    METRICS_READ = "metrics:read"


# Role → permission mapping
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: set(Permission),  # All permissions
    UserRole.ANALYST: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_START,
        Permission.SCAN_READ,
        Permission.SCAN_WRITE,
        Permission.GRAPH_READ,
        Permission.METRICS_READ,
    },
    UserRole.VIEWER: {
        Permission.PROJECT_READ,
        Permission.SCAN_READ,
        Permission.GRAPH_READ,
    },
}


def get_role_permissions(role: UserRole) -> Set[Permission]:
    """Return the set of permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_role_permissions(role)


def require_permission(permission: Permission):
    """
    FastAPI dependency factory.

    Usage::

        @router.post("/projects")
        async def create(
            _: None = Depends(require_permission(Permission.PROJECT_CREATE)),
            ...
        ):
    """
    def _check(role_str: str = UserRole.VIEWER.value) -> None:
        """Default to least-privileged role (viewer) if none is provided."""
        try:
            role = UserRole(role_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unknown role: {role_str}",
            )
        if not has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' does not have permission '{permission}'",
            )
    return _check


def require_role(*roles: UserRole):
    """
    FastAPI dependency factory that restricts access to specific roles.

    Usage::

        @router.delete("/users/{id}")
        async def delete_user(
            _: None = Depends(require_role(UserRole.ADMIN)),
            ...
        ):
    """
    allowed = set(roles)

    def _check(role_str: str = UserRole.VIEWER.value) -> None:
        """Default to least-privileged role (viewer) if none is provided."""
        try:
            role = UserRole(role_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unknown role: {role_str}",
            )
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is not authorized for this action",
            )
    return _check

"""
auth.py – Authentication API endpoints (refactored to use AuthService / Prisma)

Day 15 of YEAR_01_GAP_COVERAGE_PLAN:
  - /register  → AuthService.register()
  - /login     → AuthService.login()
  - /me        → AuthService.get_user_by_id()
  - /refresh   → AuthService.refresh()
  - /logout    → AuthService.logout()
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.db.prisma_client import get_prisma
from app.schemas import Message, Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# ---------------------------------------------------------------------------
# Backward-compat stub so conftest.py import still succeeds.
# The in-memory dict is no longer used by the endpoints; it exists only to
# avoid AttributeError in test setup code that references auth.users_db.
# ---------------------------------------------------------------------------
users_db: dict = {}


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

async def get_auth_service() -> AuthService:
    """FastAPI dependency – builds an AuthService backed by the Prisma DB."""
    db = await get_prisma()
    return AuthService(db)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """Extract and validate the bearer token; return the subject (user_id)."""
    payload = decode_token(credentials.credentials)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return user_id


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    svc: AuthService = Depends(get_auth_service),
):
    """
    Register a new user.

    - **email**: Unique e-mail address
    - **username**: Unique username (3-50 alphanumeric chars)
    - **password**: At least 8 characters
    - **full_name**: Optional display name
    """
    try:
        user = await svc.register(user_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    svc: AuthService = Depends(get_auth_service),
):
    """
    Authenticate with username + password.

    Returns a JWT **access token** (short-lived) and a **refresh token**
    (long-lived, stored server-side for revocation support).
    """
    try:
        token = await svc.login(credentials.username, credentials.password)
    except ValueError as exc:
        detail = str(exc)
        if "inactive" in detail:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
    return token


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    svc: AuthService = Depends(get_auth_service),
):
    """Return the currently authenticated user's profile."""
    user = await svc.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    svc: AuthService = Depends(get_auth_service),
):
    """
    Issue a new token pair from a valid (non-revoked) refresh token.

    The old refresh token is revoked and replaced atomically.
    """
    try:
        token = await svc.refresh(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return token


@router.post("/logout", response_model=Message)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    svc: AuthService = Depends(get_auth_service),
):
    """
    Revoke the supplied refresh token (logout from this device).

    Pass the **refresh** token (not the access token).
    """
    await svc.logout(credentials.credentials)
    return Message(message="Logged out successfully")


@router.post("/logout-all", response_model=Message)
async def logout_all(
    user_id: str = Depends(get_current_user_id),
    svc: AuthService = Depends(get_auth_service),
):
    """Revoke **all** refresh tokens for the current user (logout everywhere)."""
    await svc.logout_all(user_id)
    return Message(message="Logged out from all devices")

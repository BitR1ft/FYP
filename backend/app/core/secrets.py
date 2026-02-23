"""
Secrets management utilities.

Validates required secrets at startup, provides rotation hints, and is
designed to be vault-ready (all secrets loaded exclusively from environment
variables — no hard-coded fallbacks in production).
"""
import logging
import os
import secrets
from typing import Optional

logger = logging.getLogger(__name__)

# Minimum lengths for secrets (enforced when ENVIRONMENT=production)
_MIN_SECRET_KEY_LEN = 32
_MIN_PASSWORD_LEN = 16

class SecretsValidationError(ValueError):
    """Raised when a required secret fails validation."""

def validate_secrets(environment: str = "development") -> None:
    """
    Validate that all required secrets are present and meet minimum standards.

    In production, raises SecretsValidationError for any violation.
    In other environments, logs a warning instead so local dev is not blocked.

    Checks:
    - SECRET_KEY: present, >= 32 chars
    - POSTGRES_PASSWORD: present, >= 16 chars in production
    - NEO4J_PASSWORD: present, >= 16 chars in production
    """
    is_prod = environment.lower() == "production"
    errors: list[str] = []

    secret_key = os.getenv("SECRET_KEY", "")
    if not secret_key:
        errors.append("SECRET_KEY is not set")
    elif len(secret_key) < _MIN_SECRET_KEY_LEN:
        errors.append(f"SECRET_KEY is too short (min {_MIN_SECRET_KEY_LEN} chars)")

    for var in ("POSTGRES_PASSWORD", "NEO4J_PASSWORD"):
        val = os.getenv(var, "")
        if is_prod and len(val) < _MIN_PASSWORD_LEN:
            errors.append(f"{var} is too short for production (min {_MIN_PASSWORD_LEN} chars)")

    if errors:
        msg = "Secrets validation failed: " + "; ".join(errors)
        if is_prod:
            raise SecretsValidationError(msg)
        logger.warning(msg)

def generate_secret(length: int = 64) -> str:
    """Generate a cryptographically secure random secret string."""
    return secrets.token_urlsafe(length)

def rotation_hint(secret_name: str) -> str:
    """Return a human-readable hint for rotating a named secret."""
    return (
        f"To rotate {secret_name}: "
        "1) generate a new value with `generate_secret()`, "
        "2) update it in your secrets manager / .env, "
        "3) restart all services that consume it."
    )

"""Tests for Week 25 security hardening features."""
import pytest
from unittest.mock import patch, MagicMock
import json
import time

# Day 158: Secrets
from app.core.secrets import validate_secrets, generate_secret, SecretsValidationError

# Day 159: RBAC
from app.core.rbac import UserRole, Permission, has_permission, get_role_permissions

# Day 160: Audit Logging
from app.core.audit import log_audit, AuditAction

# Day 161: Rate Limiting
from app.core.rate_limit import SlidingWindowRateLimiter

# Day 162: WAF
from app.core.waf import check_for_attacks, sanitize_string

# --- Day 158: Secrets ---
def test_generate_secret_returns_string():
    s = generate_secret()
    assert isinstance(s, str) and len(s) > 32

def test_validate_secrets_warns_in_dev(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "short")
    monkeypatch.setenv("POSTGRES_PASSWORD", "")
    # In dev, should warn but not raise
    validate_secrets("development")  # no exception

def test_validate_secrets_raises_in_prod(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "tooshort")
    with pytest.raises(SecretsValidationError):
        validate_secrets("production")

def test_validate_secrets_passes_with_good_values(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a" * 40)
    monkeypatch.setenv("POSTGRES_PASSWORD", "b" * 20)
    monkeypatch.setenv("NEO4J_PASSWORD", "c" * 20)
    validate_secrets("production")  # no exception

# --- Day 159: RBAC ---
def test_admin_has_all_permissions():
    for perm in Permission:
        assert has_permission(UserRole.ADMIN, perm)

def test_viewer_read_only():
    assert has_permission(UserRole.VIEWER, Permission.PROJECT_READ)
    assert not has_permission(UserRole.VIEWER, Permission.PROJECT_CREATE)
    assert not has_permission(UserRole.VIEWER, Permission.PROJECT_DELETE)

def test_analyst_can_create_projects():
    assert has_permission(UserRole.ANALYST, Permission.PROJECT_CREATE)
    assert not has_permission(UserRole.ANALYST, Permission.USER_MANAGE)

def test_get_role_permissions_returns_set():
    perms = get_role_permissions(UserRole.ANALYST)
    assert isinstance(perms, set)
    assert len(perms) > 0

# --- Day 160: Audit Logging ---
def test_log_audit_emits_json():
    with patch("app.core.audit.audit_logger") as mock_logger:
        log_audit(
            AuditAction.USER_LOGIN,
            actor_id="user-123",
            ip_address="127.0.0.1",
            correlation_id="req-abc",
            success=True,
        )
        mock_logger.info.assert_called_once()
        raw = mock_logger.info.call_args[0][0]
        entry = json.loads(raw)
        assert entry["action"] == AuditAction.USER_LOGIN
        assert entry["actor_id"] == "user-123"
        assert entry["success"] is True

def test_log_audit_failed_action():
    with patch("app.core.audit.audit_logger") as mock_logger:
        log_audit(AuditAction.USER_LOGIN_FAILED, success=False, ip_address="1.2.3.4")
        raw = mock_logger.info.call_args[0][0]
        entry = json.loads(raw)
        assert entry["success"] is False

# --- Day 161: Rate Limiting ---
def test_rate_limiter_allows_within_limit():
    limiter = SlidingWindowRateLimiter(max_calls=5, window_seconds=60, name="test")
    for _ in range(5):
        allowed, _ = limiter.is_allowed("user1")
        assert allowed

def test_rate_limiter_blocks_over_limit():
    limiter = SlidingWindowRateLimiter(max_calls=3, window_seconds=60, name="test")
    for _ in range(3):
        limiter.is_allowed("user2")
    allowed, remaining = limiter.is_allowed("user2")
    assert not allowed
    assert remaining == 0

def test_rate_limiter_independent_keys():
    limiter = SlidingWindowRateLimiter(max_calls=1, window_seconds=60, name="test")
    allowed_a, _ = limiter.is_allowed("keyA")
    allowed_b, _ = limiter.is_allowed("keyB")
    assert allowed_a and allowed_b

def test_rate_limiter_window_expiry():
    limiter = SlidingWindowRateLimiter(max_calls=1, window_seconds=1, name="test")
    limiter.is_allowed("expiry_key")
    time.sleep(1.1)
    allowed, _ = limiter.is_allowed("expiry_key")
    assert allowed

# --- Day 162: WAF ---
def test_waf_blocks_sql_injection():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        check_for_attacks("SELECT * FROM users", "query")
    assert exc_info.value.status_code == 400

def test_waf_blocks_xss():
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        check_for_attacks("<script>alert(1)</script>", "body")

def test_waf_blocks_path_traversal():
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        check_for_attacks("../../etc/passwd", "path")

def test_waf_allows_clean_input():
    check_for_attacks("example.com", "target")  # no exception
    check_for_attacks("My Pentest Project", "name")

def test_sanitize_string_strips_whitespace():
    assert sanitize_string("  hello  ") == "hello"

def test_sanitize_string_removes_null_bytes():
    assert "\x00" not in sanitize_string("hello\x00world")

# Security Guide

## Secrets Management

All secrets are loaded exclusively from environment variables.
Run `python -c "from app.core.secrets import generate_secret; print(generate_secret())"` 
to generate a new secret.

### Required Secrets

| Variable | Description | Min Length |
|----------|-------------|-----------|
| `SECRET_KEY` | JWT signing key | 32 chars |
| `POSTGRES_PASSWORD` | Database password | 16 chars (prod) |
| `NEO4J_PASSWORD` | Graph DB password | 16 chars (prod) |
| `GRAFANA_PASSWORD` | Grafana admin password | required |

## RBAC

Three built-in roles:

| Role | Permissions |
|------|-------------|
| `admin` | All permissions |
| `analyst` | Create/read/update/start projects, read/write scans, read graph, read metrics |
| `viewer` | Read projects, read scans, read graph |

## Audit Logging

Sensitive operations are written to the `autopentestai.audit` logger as
structured JSON. Configure this logger to write to a separate file or SIEM.

Audited events: user registration, login (success/fail), logout, token refresh,
password change, project create/update/delete/start, permission denied, rate limit hit.

## Rate Limiting

| Limiter | Limit | Window |
|---------|-------|--------|
| User API | 60 req | 1 min |
| Project start | 10 | 1 hour |
| Login (per IP) | 5 attempts | 15 min |

## WAF

Query parameters are scanned for SQL injection, XSS, and path traversal patterns.
Matching requests receive HTTP 400.

## Security Headers

All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`

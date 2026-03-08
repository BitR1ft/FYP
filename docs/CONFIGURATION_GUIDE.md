# AutoPenTest AI — Configuration Guide

> **Day 204 · Phase K: Documentation**
> Complete reference for every environment variable, configuration file, and
> runtime option in AutoPenTest AI.

---

## Table of Contents

1. [Environment Variables Reference](#environment-variables-reference)
2. [Configuration Files](#configuration-files)
3. [Feature Flags](#feature-flags)
4. [Rate Limiting Configuration](#rate-limiting-configuration)
5. [AI Agent Configuration](#ai-agent-configuration)
6. [Security Configuration](#security-configuration)
7. [Observability Configuration](#observability-configuration)
8. [Docker Compose Overrides](#docker-compose-overrides)
9. [Environment-Specific Best Practices](#environment-specific-best-practices)

---

## Environment Variables Reference

Copy `.env.example` to `.env` and configure each section below.

### Core Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ | — | 32-byte hex secret for JWT signing. Generate: `openssl rand -hex 32` |
| `ENVIRONMENT` | ✅ | `production` | One of `development`, `testing`, `staging`, `production` |
| `DEBUG` | — | `false` | Enable debug logging. **Never true in production** |
| `ALLOWED_ORIGINS` | — | `http://localhost:3000` | Comma-separated CORS allowed origins |
| `API_PREFIX` | — | `/api/v1` | URL prefix for all API routes |
| `APP_NAME` | — | `AutoPenTest AI` | Application name shown in docs |

### Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL DSN, e.g. `postgresql+asyncpg://user:pass@host:5432/db` |
| `DB_POOL_SIZE` | — | `20` | SQLAlchemy connection pool size |
| `DB_MAX_OVERFLOW` | — | `10` | Additional connections beyond pool size |
| `DB_POOL_TIMEOUT` | — | `30` | Seconds to wait for a connection from pool |
| `DB_ECHO` | — | `false` | Log all SQL statements (development only) |

### Neo4j Graph Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEO4J_URI` | ✅ | — | Bolt URI, e.g. `bolt://neo4j:7687` |
| `NEO4J_USER` | ✅ | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | ✅ | — | Neo4j password |
| `NEO4J_DATABASE` | — | `neo4j` | Database name (Enterprise: custom databases) |
| `NEO4J_MAX_CONNECTION_POOL_SIZE` | — | `50` | Max concurrent Neo4j connections |

### Authentication & Security

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_ALGORITHM` | — | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | — | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | — | `7` | Refresh token TTL |
| `BCRYPT_ROUNDS` | — | `12` | bcrypt work factor (≥10 in production) |
| `WAF_ENABLED` | — | `true` | Enable WAF middleware (SQL injection / XSS detection) |
| `RATE_LIMIT_ENABLED` | — | `true` | Enable sliding-window rate limiting |

### AI Providers

At least one AI provider must be configured for the agent to function.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ⚠️ | — | OpenAI API key (GPT-4o default model) |
| `OPENAI_MODEL` | — | `gpt-4o` | OpenAI model name |
| `ANTHROPIC_API_KEY` | ⚠️ | — | Anthropic API key (Claude fallback) |
| `ANTHROPIC_MODEL` | — | `claude-3-5-sonnet-20241022` | Anthropic model name |
| `AI_TEMPERATURE` | — | `0.1` | LLM sampling temperature (0–1) |
| `AI_MAX_TOKENS` | — | `4096` | Max tokens per LLM response |
| `AI_MAX_ITERATIONS` | — | `20` | Max ReAct loop iterations per agent session |
| `AI_TIMEOUT_SECONDS` | — | `300` | Total timeout for one agent task |

### LangSmith (optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LANGCHAIN_TRACING_V2` | — | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | — | — | LangSmith API key |
| `LANGCHAIN_PROJECT` | — | `autopentestai` | LangSmith project name |

### Tool Execution

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TOOL_EXECUTION_TIMEOUT` | — | `300` | Seconds before a tool subprocess is killed |
| `TOOL_MAX_CONCURRENT` | — | `3` | Max simultaneous tool processes per user |
| `KALI_IMAGE` | — | `kalilinux/kali-rolling` | Docker image for Kali tool sandbox |
| `TOOL_NETWORK_MODE` | — | `bridge` | Docker network mode for tool containers |
| `TOOL_MEMORY_LIMIT` | — | `512m` | Memory limit for each tool container |
| `TOOL_CPU_QUOTA` | — | `100000` | CPU quota (100000 = 1 core) |

### Frontend (Next.js — prefix `NEXT_PUBLIC_` for client-side)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | `http://localhost:8000` | Backend API base URL |
| `NEXT_PUBLIC_WS_URL` | ✅ | `ws://localhost:8000` | WebSocket base URL |
| `NEXT_PUBLIC_APP_NAME` | — | `AutoPenTest AI` | Branding name |
| `NEXT_PUBLIC_ENABLE_REGISTRATION` | — | `true` | Show registration form |
| `NEXT_PUBLIC_MAX_UPLOAD_MB` | — | `10` | Max file upload size shown to users |

### Observability

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OTEL_ENABLED` | — | `false` | Enable OpenTelemetry tracing |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | `http://jaeger:4317` | OTLP gRPC endpoint |
| `OTEL_SERVICE_NAME` | — | `autopentestai-backend` | Service name in traces |
| `PROMETHEUS_ENABLED` | — | `true` | Expose `/metrics` endpoint |
| `GRAFANA_PASSWORD` | — | `admin` | Grafana admin password (change in production!) |

### Email (optional — for alerts)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_HOST` | — | — | SMTP server hostname |
| `SMTP_PORT` | — | `587` | SMTP port |
| `SMTP_USER` | — | — | SMTP username |
| `SMTP_PASSWORD` | — | — | SMTP password |
| `SMTP_FROM` | — | `noreply@autopentestai.local` | From address for system emails |
| `ALERT_EMAIL_TO` | — | — | Comma-separated alert recipients |

---

## Configuration Files

### `.env` / `.env.example`

Root-level file loaded by Docker Compose. Copy to `.env` and edit before first run.

```bash
cp .env.example .env
$EDITOR .env
```

### `backend/.env` (local dev only)

Optional backend-only overrides when running the API server directly with uvicorn.
Takes precedence over the root `.env` when the backend process loads it via
`python-dotenv`.

### `frontend/.env.local` (local dev only)

Next.js local dev overrides. Values prefixed with `NEXT_PUBLIC_` are exposed to
the browser bundle.

```bash
cp frontend/.env.local.example frontend/.env.local
```

### `docker-compose.yml`

Default stack configuration (development). Do not store secrets directly in this
file — use `.env` interpolation (`${VAR}`).

### `docker/staging/docker-compose.staging.yml`

Extends the base compose file with staging-specific resource limits and reduced
replica counts. Use:

```bash
docker compose -f docker-compose.yml -f docker/staging/docker-compose.staging.yml up -d
```

### `docker/production/docker-compose.production.yml`

Production configuration: 2 backend replicas, Nginx TLS termination, nightly
pg_dump sidecar, strict resource limits. See [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md).

---

## Feature Flags

Control optional features via environment variables without redeploying code.

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `ENABLE_CHAOS_MODE` | `true`/`false` | `false` | Enable chaos engineering endpoints (dev/staging only) |
| `ENABLE_GRAPH_EXPORT` | `true`/`false` | `true` | Allow graph export (GEXF, JSON) |
| `ENABLE_AUTO_EXPLOIT` | `true`/`false` | `false` | Enable autonomous exploitation (requires human approval) |
| `ENABLE_SUBDOMAIN_BRUTE` | `true`/`false` | `true` | Allow subdomain brute-forcing |
| `ENABLE_SELF_REGISTRATION` | `true`/`false` | `true` | Allow new users to register |
| `ENABLE_MULTI_TENANCY` | `true`/`false` | `false` | Enforce project-level tenant isolation |
| `ENABLE_AUDIT_LOG` | `true`/`false` | `true` | Persist audit events to structured log |
| `ENABLE_RATE_LIMITING` | `true`/`false` | `true` | API rate limiting middleware |

---

## Rate Limiting Configuration

Rate limits are configured in `backend/app/core/rate_limit.py` and can be tuned
via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_USER_RPM` | `60` | General API requests per minute per user |
| `RATE_LIMIT_SCAN_RPH` | `10` | Scan-start requests per hour per user |
| `RATE_LIMIT_LOGIN_ATTEMPTS` | `5` | Login attempts per 15 minutes per IP |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Default sliding-window duration |

To disable rate limiting globally (e.g., during load tests):

```bash
RATE_LIMIT_ENABLED=false
```

---

## AI Agent Configuration

### Model selection

The agent uses a priority-based provider selection:

1. `OPENAI_API_KEY` set → GPT-4o
2. `ANTHROPIC_API_KEY` set → Claude 3.5 Sonnet
3. Neither set → agent raises `ConfigurationError` at startup

Override per-request via the API:

```json
POST /api/v1/agent/chat
{
  "message": "...",
  "model_override": "gpt-4o-mini"
}
```

### Safety limits

```dotenv
AI_MAX_ITERATIONS=20           # Hard cap on ReAct loop steps
AI_TIMEOUT_SECONDS=300         # Wall-clock timeout per task
APPROVAL_REQUIRED_RISK=high    # Risk level requiring human approval: low/medium/high/critical
```

### Risk tiers

| Tier | Examples | Behaviour |
|------|----------|-----------|
| `low` | subdomain enum, banner grab | Auto-execute |
| `medium` | full port scan, web crawl | Auto-execute with audit log |
| `high` | vulnerability exploit PoC | Pause, request human approval |
| `critical` | data exfiltration, destruction | Blocked by default |

---

## Security Configuration

### Secrets rotation

Rotate all secrets on this schedule (see [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md)):

| Secret | Rotation Period |
|--------|----------------|
| `SECRET_KEY` | 90 days |
| Database passwords | 90 days |
| Neo4j password | 90 days |
| API keys (OpenAI, Anthropic) | As needed |
| Grafana password | 90 days |

### TLS (production)

In production, Nginx handles TLS termination. Configure certificates in
`docker/production/nginx/`:

```
docker/production/nginx/
├── nginx.conf
├── certs/
│   ├── fullchain.pem   ← place your cert here
│   └── privkey.pem     ← place your key here
```

### Allowed hosts

```dotenv
ALLOWED_HOSTS=autopentestai.example.com,www.autopentestai.example.com
```

Leave empty to allow all hosts (development only).

---

## Observability Configuration

### Prometheus

Prometheus scrapes `/metrics` every 15 seconds by default.  
To change the interval, edit `docker/monitoring/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'autopentestai-backend'
    scrape_interval: 30s     # ← change here
```

### Grafana dashboards

Dashboards are auto-provisioned from `docker/monitoring/grafana/provisioning/`.
To add custom dashboards, drop JSON files into
`docker/monitoring/grafana/dashboards/` and restart Grafana.

### OpenTelemetry (optional)

```dotenv
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_SERVICE_NAME=autopentestai-backend
```

Add Jaeger to your compose file:

```yaml
jaeger:
  image: jaegertracing/all-in-one:1.57
  ports:
    - "16686:16686"
    - "4317:4317"
```

---

## Docker Compose Overrides

Create a `docker-compose.override.yml` (git-ignored) for local tweaks without
modifying the tracked compose file:

```yaml
# docker-compose.override.yml
services:
  backend:
    environment:
      DEBUG: "true"
      DB_ECHO: "true"
    volumes:
      - ./backend:/app   # live code mount for hot-reload
  frontend:
    environment:
      NEXT_PUBLIC_API_URL: "http://localhost:8000"
```

Docker Compose automatically merges `docker-compose.override.yml`.

---

## Environment-Specific Best Practices

### Development

```dotenv
ENVIRONMENT=development
DEBUG=true
DB_ECHO=false        # only enable when debugging SQL
SECRET_KEY=dev-only-secret-not-secure
GRAFANA_PASSWORD=admin
RATE_LIMIT_ENABLED=false   # easier testing
```

### Staging

```dotenv
ENVIRONMENT=staging
DEBUG=false
SECRET_KEY=<32-byte random>
GRAFANA_PASSWORD=<strong password>
RATE_LIMIT_ENABLED=true
OTEL_ENABLED=true
```

### Production

```dotenv
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<32-byte random, rotated quarterly>
GRAFANA_PASSWORD=<strong password>
RATE_LIMIT_ENABLED=true
WAF_ENABLED=true
OTEL_ENABLED=true
BCRYPT_ROUNDS=14      # higher work factor
```

> ⚠️ **Never** commit `.env` to source control. It is in `.gitignore` by default.

---

*Last updated: Week 31 — Day 204*

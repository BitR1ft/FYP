# AutoPenTest AI — API Reference (Extended)

> **Day 196: OpenAPI Documentation — Complete Endpoint Reference**
>
> This document extends the base `docs/API.md` with comprehensive OpenAPI
> descriptions, request/response examples, and error handling documentation.
> The live interactive docs are available at `/docs` (Swagger UI) and
> `/redoc` (ReDoc) when the backend is running.

---

## 📋 Base Information

| Property | Value |
|----------|-------|
| Base URL (dev) | `http://localhost:8000` |
| Base URL (production) | `https://api.autopentestai.example.com` |
| API Version | `v1` |
| OpenAPI Version | `3.1.0` |
| Authentication | JWT Bearer Token |
| Content-Type | `application/json` |

---

## 🔑 Authentication

All protected endpoints require a JWT access token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Lifecycle

```
POST /api/auth/login
  → access_token (30 min TTL)
  → refresh_token (7 days TTL)

When access_token expires:
POST /api/auth/refresh
  → new access_token
  → rotated refresh_token

POST /api/auth/logout
  → revokes refresh_token
```

---

## 📚 Endpoint Groups

### Auth Endpoints (`/api/auth/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register new user |
| POST | `/api/auth/login` | None | Login & get tokens |
| POST | `/api/auth/refresh` | None (RT) | Refresh access token |
| POST | `/api/auth/logout` | Bearer | Revoke refresh token |
| GET | `/api/auth/me` | Bearer | Get current user |
| PUT | `/api/auth/me` | Bearer | Update user profile |
| PUT | `/api/auth/me/password` | Bearer | Change password |

### Project Endpoints (`/api/projects/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/projects` | Bearer | List projects (paginated) |
| POST | `/api/projects` | Bearer | Create project |
| GET | `/api/projects/{id}` | Bearer | Get project details |
| PUT | `/api/projects/{id}` | Bearer | Update project |
| DELETE | `/api/projects/{id}` | Bearer | Delete project |
| POST | `/api/projects/{id}/start` | Bearer | Start recon scan |
| POST | `/api/projects/{id}/stop` | Bearer | Stop active scan |
| GET | `/api/projects/{id}/tasks` | Bearer | List project tasks |

### Recon Endpoints (`/api/recon/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/recon/{project_id}/subdomains` | Bearer | List discovered subdomains |
| GET | `/api/recon/{project_id}/ports` | Bearer | List open ports |
| GET | `/api/recon/{project_id}/http` | Bearer | List HTTP endpoints |
| GET | `/api/recon/{project_id}/technologies` | Bearer | List detected technologies |

### Graph Endpoints (`/api/graph/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/graph/{project_id}/attack-surface` | Bearer | Full attack surface graph |
| GET | `/api/graph/{project_id}/stats` | Bearer | Graph statistics |
| GET | `/api/graph/{project_id}/vulnerabilities` | Bearer | Vulnerability nodes |
| GET | `/api/graph/{project_id}/technologies` | Bearer | Technology nodes |
| GET | `/api/graph/health` | Bearer | Neo4j health check |

### Vulnerability Endpoints (`/api/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/cve/{cve_id}` | Bearer | Get CVE details |
| GET | `/api/cve/search` | Bearer | Search CVEs |
| GET | `/api/enrichment/{project_id}` | Bearer | Get enrichment data |

### AI Agent Endpoints (`/api/agent/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/agent/chat` | Bearer | Chat with AI agent |
| GET | `/api/agent/sessions` | Bearer | List agent sessions |
| GET | `/api/agent/sessions/{id}` | Bearer | Get session details |
| POST | `/api/agent/approve` | Bearer | Approve pending tool call |
| POST | `/api/agent/reject` | Bearer | Reject pending tool call |

### Observability

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Health check |
| GET | `/metrics` | None | Prometheus metrics |

---

## 📝 Detailed Endpoint Documentation

### POST /api/auth/login

Login with username and password to receive JWT tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "SecurePassword1!"
}
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 401 | `INVALID_CREDENTIALS` | Wrong username or password |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many login attempts (5/15 min) |
| 422 | `VALIDATION_ERROR` | Missing or malformed fields |

---

### GET /api/projects

List all projects for the authenticated user with optional filtering.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 10 | Results per page (max 100) |
| `status` | string | null | Filter: `draft`, `running`, `paused`, `completed`, `failed` |
| `search` | string | null | Search in name and description |
| `sort` | string | `created_at` | Sort field: `created_at`, `name`, `status`, `updated_at` |
| `order` | string | `desc` | Sort order: `asc` or `desc` |

**Response: 200 OK**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Example Corp Recon",
      "target": "example.com",
      "status": "completed",
      "description": "Full reconnaissance of example.com",
      "enable_subdomain_enum": true,
      "enable_port_scan": true,
      "enable_web_crawl": true,
      "enable_tech_detection": true,
      "enable_vuln_scan": true,
      "enable_nuclei": true,
      "enable_auto_exploit": false,
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-01T12:00:00Z",
      "user_id": "user-uuid"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 10,
  "pages": 5
}
```

---

### POST /api/projects

Create a new reconnaissance project.

**Request:**
```json
{
  "name": "Target Corp Assessment",
  "target": "targetcorp.com",
  "description": "Full attack surface assessment",
  "enable_subdomain_enum": true,
  "enable_port_scan": true,
  "enable_web_crawl": true,
  "enable_tech_detection": true,
  "enable_vuln_scan": true,
  "enable_nuclei": true,
  "enable_auto_exploit": false,
  "config": {
    "port_scan_type": "full",
    "nuclei_severity": ["critical", "high", "medium"],
    "max_crawl_depth": 5,
    "concurrent_scans": 3
  }
}
```

**Response: 201 Created**
```json
{
  "id": "new-project-uuid",
  "name": "Target Corp Assessment",
  "target": "targetcorp.com",
  "status": "draft",
  "created_at": "2026-01-01T10:00:00Z"
}
```

---

### POST /api/projects/{id}/start

Start the reconnaissance scan for a project.

**Requirements:**
- Project must be in `draft` or `paused` state
- User must have `PROJECT_START` permission

**Response: 200 OK**
```json
{
  "id": "project-uuid",
  "status": "queued",
  "message": "Scan queued successfully",
  "started_at": "2026-01-01T10:00:00Z"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_STATE` | Project is not in draft or paused state |
| 403 | `PERMISSION_DENIED` | User cannot start scans |
| 409 | `ALREADY_RUNNING` | Project scan is already running |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many scan starts (10/hr) |

---

### GET /api/graph/{project_id}/attack-surface

Retrieve the complete attack surface graph for a project.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_nodes` | integer | Limit number of nodes returned (default: 500) |
| `include_types` | string[] | Node types to include |

**Response: 200 OK**
```json
{
  "nodes": [
    {
      "id": "Domain:example.com",
      "type": "Domain",
      "label": "example.com",
      "properties": {
        "name": "example.com",
        "created_at": "2026-01-01T10:00:00Z"
      }
    }
  ],
  "edges": [
    {
      "source": "Domain:example.com",
      "target": "Subdomain:api.example.com",
      "type": "HAS_SUBDOMAIN"
    }
  ],
  "stats": {
    "total_nodes": 42,
    "total_edges": 87,
    "node_types": {
      "Domain": 1,
      "Subdomain": 15,
      "IPAddress": 8,
      "Port": 18
    }
  }
}
```

---

## 🚨 Error Response Format

All API errors follow a consistent format:

```json
{
  "detail": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many login attempts. Try again in 15 minutes.",
    "retry_after": 900
  }
}
```

## 🔄 Pagination

Paginated endpoints use consistent query parameters and response format:

```
GET /api/projects?page=2&page_size=20
```

```json
{
  "items": [...],
  "total": 100,
  "page": 2,
  "page_size": 20,
  "pages": 5
}
```

## ⚡ Rate Limiting

| Endpoint Group | Limit | Window |
|----------------|-------|--------|
| Login | 5 requests | 15 minutes |
| Project Start | 10 requests | 1 hour |
| General API | 60 requests | 1 minute |

Rate limit headers are included in every response:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1704067260
```

---

*Updated: Week 30, Day 196 — Phase K: API Documentation Complete* ✅

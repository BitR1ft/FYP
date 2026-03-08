# AutoPenTest AI — System Architecture Documentation

> **Day 202: Architecture Documentation — Complete System Design**
>
> Comprehensive system architecture documentation including component
> interactions, data flow, deployment architecture, and design decisions.

---

## 🏗️ System Overview

AutoPenTest AI is a **full-stack AI-powered penetration testing assistant**
that automates the reconnaissance and vulnerability assessment phases of
security testing, guided by an LLM-powered AI agent.

### Core Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Next.js 14 + TypeScript | Web UI for users |
| **Backend API** | FastAPI (Python 3.11) | Core API server |
| **AI Agent** | LangChain + GPT-4 | Autonomous assessment |
| **Graph DB** | Neo4j 5.15 | Attack surface graph |
| **Relational DB** | PostgreSQL 16 | User/project data |
| **MCP Servers** | Python + MCP Protocol | Tool execution layer |
| **Observability** | Prometheus + Grafana | Metrics + alerting |
| **Tracing** | OpenTelemetry | Distributed tracing |

---

## 🗺️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                 │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │ HTTPS/WSS
                         ┌───────▼──────┐
                         │    Nginx     │
                         │ (TLS Termination│
                         │ Load Balancer)│
                         └──┬───────┬───┘
                            │       │
               ┌────────────▼┐     ┌▼────────────┐
               │  Next.js    │     │  FastAPI    │
               │  Frontend   │     │  Backend    │
               │  (Port 3000)│     │  (Port 8000)│
               └────────────┘     └──────┬──────┘
                                         │
              ┌──────────────────────────┤
              │                          │
     ┌────────▼──────┐        ┌─────────▼──────┐
     │  PostgreSQL   │        │    Neo4j        │
     │  (Port 5432)  │        │  (Port 7687)   │
     │  User/Project │        │  Attack Graph  │
     └───────────────┘        └────────────────┘
              │
     ┌────────▼──────────────────────────────────┐
     │           Security Tools Layer             │
     │  ┌────────┐ ┌────────┐ ┌────────────────┐ │
     │  │ Naabu  │ │ Nuclei │ │  Metasploit    │ │
     │  │ MCP    │ │ MCP    │ │  MCP Server    │ │
     │  │ Server │ │ Server │ │  (Port 8003)   │ │
     │  └────────┘ └────────┘ └────────────────┘ │
     └───────────────────────────────────────────┘
              │
     ┌────────▼──────────────────────────────────┐
     │           Observability Stack              │
     │  ┌──────────────┐  ┌─────────────────┐    │
     │  │  Prometheus  │  │     Grafana      │   │
     │  │  (Port 9090) │  │   (Port 3001)   │   │
     │  └──────────────┘  └─────────────────┘   │
     └───────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagrams

### Scan Initiation Flow

```
User clicks "Start Scan"
        │
        ▼
Frontend validates project state
        │
        ▼
POST /api/projects/{id}/start
        │
        ▼
Auth middleware validates JWT + RBAC (PROJECT_START permission)
        │
        ▼
WAF middleware checks for injection attacks
        │
        ▼
Rate limiter checks (10 starts/hour)
        │
        ▼
Project service updates status: draft → queued
        │
        ▼
Background task launched (Celery/asyncio)
        │
        ├──► Recon Phase: subfinder, amass, naabu
        ├──► Probe Phase: httpx, whatweb
        ├──► Vuln Phase: nuclei, nmap scripts
        └──► Graph Phase: ingest all results to Neo4j
        │
        ▼
SSE stream pushes progress updates to frontend
        │
        ▼
Project status updated: running → completed/failed
```

### AI Agent Chat Flow

```
User message: "What vulnerabilities did you find?"
        │
        ▼
POST /api/agent/chat
        │
        ▼
AgentSession loaded (or created)
        │
        ▼
Context built: project data + scan results + conversation history
        │
        ▼
LLM (GPT-4) generates response + optional tool call
        │
        ├─[No tool call]──► Stream text response to user via SSE
        │
        └─[Tool call]──► Check risk level
                         │
                         ├─[LOW/MEDIUM]──► Execute immediately
                         │                 └──► Stream result + agent reasoning
                         │
                         └─[HIGH/CRITICAL]──► Send approval_required event
                                              └──► Wait for user approval/rejection
```

### Graph Data Ingestion Flow

```
Tool completes (e.g., subfinder finds subdomains)
        │
        ▼
Raw output parsed to ToolResult
        │
        ▼
TaskResult stored in PostgreSQL
        │
        ▼
Graph ingestion pipeline triggered
        │
        ▼
Neo4j nodes created:
  - Domain node (if not exists)
  - Subdomain nodes
  - HAS_SUBDOMAIN relationships
        │
        ▼
Graph updated in real-time
        │
        ▼
Frontend graph view reloads on next poll/SSE event
```

---

## 🔐 Security Architecture

### Defense in Depth

```
Layer 1: Network (Nginx)
  - TLS 1.3 termination
  - DDoS protection
  - IP rate limiting

Layer 2: Application Gateway
  - JWT authentication
  - RBAC authorization
  - WAF (SQL injection, XSS, path traversal)

Layer 3: Business Logic
  - Input validation (Pydantic)
  - Sliding window rate limiting
  - Audit logging

Layer 4: Data
  - Encrypted at rest (PostgreSQL + Neo4j)
  - Row-level security (user_id isolation)
  - Secret management (environment variables)

Layer 5: Operations
  - Secret rotation
  - Dependency scanning (Dependabot)
  - Container scanning (Trivy)
  - SAST (Bandit + CodeQL)
```

---

## 🌐 Network Segmentation

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Networks                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  prod-db (internal, no external access)                  │  │
│  │  172.20.1.0/24                                           │  │
│  │  postgres ◄──► neo4j ◄──► backend                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  prod-backend                                            │  │
│  │  172.20.2.0/24                                           │  │
│  │  backend ◄──► prometheus                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  prod-frontend (internet-accessible)                     │  │
│  │  172.20.3.0/24                                           │  │
│  │  nginx ◄──► frontend ◄──► backend                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  tools-network (isolated, controlled access)             │  │
│  │  172.20.4.0/24                                           │  │
│  │  kali-tools ◄──► recon-container ◄──► backend           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Performance Architecture

### Caching Strategy

| Layer | Cache | TTL | What's Cached |
|-------|-------|-----|---------------|
| CDN | Nginx `proxy_cache` | 1 hour | Static assets |
| Application | In-memory dict | 5 min | CVE enrichment data |
| Database | PostgreSQL buffer | Runtime | Hot query results |
| Graph | Neo4j page cache | Runtime | Frequently traversed paths |

### Async Architecture

The backend uses **async Python** throughout:

```python
# FastAPI endpoints are all async
@router.get("/projects")
async def list_projects(db: AsyncPrismaClient):
    return await db.project.find_many()

# Background tasks use asyncio
async def run_recon_phase(project_id: str):
    results = await asyncio.gather(
        run_subfinder(target),
        run_amass(target),
        run_naabu(target),
    )
```

### Database Connection Pooling

- **PostgreSQL**: Connection pool managed by Prisma (default: 10 connections)
- **Neo4j**: Connection pool via official Python driver (default: 5 connections)

---

## 📦 Deployment Architecture

### Container Topology (Production)

```
Load Balancer (Nginx)
    │
    ├── backend (replica 1, 2 cpus, 2GB)
    ├── backend (replica 2, 2 cpus, 2GB)
    │
    ├── frontend (replica 1, 1 cpu, 1GB)
    ├── frontend (replica 2, 1 cpu, 1GB)
    │
    ├── postgres (single, 4 cpus, 4GB)
    │       └── backup service
    │
    ├── neo4j (single, 4 cpus, 6GB)
    │
    └── tools (isolated)
            ├── kali-tools (4 cpus, 4GB)
            └── recon-container (2 cpus, 2GB)
```

### Blue/Green Deployment

See `.github/workflows/blue-green.yml` and `docs/OPERATIONS_RUNBOOK.md`
for the complete blue/green deployment process.

---

## 🔄 Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend language | Python 3.11 | Security ecosystem, asyncio, team expertise |
| Web framework | FastAPI | Async support, OpenAPI auto-generation, Pydantic |
| Frontend | Next.js 14 | SSR, App Router, TypeScript |
| State management | Zustand + React Query | Lightweight, composable |
| Relational DB | PostgreSQL | JSON support, reliability, community |
| Graph DB | Neo4j | Native graph queries for attack surface |
| AI agent framework | LangChain | Tool calling, memory, streaming |
| MCP Protocol | JSON-RPC 2.0 | Standardized tool interface |
| Observability | Prometheus + Grafana | Industry standard, self-hosted |
| Tracing | OpenTelemetry | Vendor-neutral distributed tracing |

---

*Updated: Week 30, Day 202 — Phase K: Architecture Documentation Complete* ✅

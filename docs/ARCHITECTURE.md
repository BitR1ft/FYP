# AutoPenTest AI Architecture

## System Overview

AutoPenTest AI is a microservices-based penetration testing framework with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                          │
│              (TypeScript, Tailwind CSS, React)                   │
│                    Port: 3000                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    REST API / WebSocket
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│                      FastAPI Backend                             │
│                   (Python, Async/Await)                          │
│                      Port: 8000                                  │
└───┬──────────────┬─────────────┬─────────────┬──────────────────┘
    │              │             │             │
    ▼              ▼             ▼             ▼
┌────────┐    ┌────────┐    ┌────────┐    ┌────────────┐
│PostgreSQL   │ Neo4j   │   │ Kali    │   │ AI Agent   │
│ (Config) │  │(Graph)  │   │ Tools   │   │(LangGraph) │
│Port: 5432│  │Port:7687│   │Container│   │            │
└──────────┘  └─────────┘   └─────────┘   └────────────┘
```

## Components

### 1. Frontend (Next.js)
- **Technology**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Features**:
  - User authentication (JWT)
  - Project management dashboard
  - Real-time scan monitoring
  - Graph visualization (to be implemented)
  - Report viewing

### 2. Backend (FastAPI)
- **Technology**: FastAPI (Python)
- **Database ORM**: Prisma
- **Features**:
  - RESTful API
  - WebSocket for real-time updates
  - JWT authentication
  - Rate limiting
  - Request validation (Pydantic)

### 3. Databases

#### PostgreSQL
- Stores application configuration
- User accounts and authentication
- Project settings
- Scan configurations

#### Neo4j
- Graph database for attack surface modeling
- Stores relationships between:
  - Domains → Subdomains
  - IPs → Ports → Services
  - URLs → Endpoints → Parameters
  - Vulnerabilities → CVEs → Exploits
  - Credentials → Access paths

### 4. Tool Containers (Future)
- **Kali Tools Container**: Nmap, Naabu, Nuclei, etc.
- **Metasploit Container**: Exploitation framework
- **Custom Tools**: MCP servers for tool integration

### 5. AI Agent (Future)
- **Framework**: LangGraph with LangChain
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Pattern**: ReAct (Reasoning + Acting)
- **Features**:
  - Multi-step reasoning
  - Tool orchestration
  - Attack path planning
  - Tree-of-Thought for exploration

## Data Flow

### 1. Project Creation
```
User → Frontend → Backend API → PostgreSQL
```

### 2. Scan Execution (Future)
```
User → Frontend → Backend → Agent → Tools → Neo4j
                     ↓
                  WebSocket
                     ↓
                  Frontend (real-time updates)
```

### 3. Report Generation (Future)
```
Backend → Neo4j (fetch data) → Report Generator → PDF/HTML
```

## Security Considerations

1. **Authentication**: JWT tokens with refresh mechanism
2. **Authorization**: Role-based access control (RBAC)
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: All inputs validated via Pydantic
5. **Scope Enforcement**: Only authorized targets can be scanned
6. **Audit Logging**: All actions logged for compliance
7. **Secrets Management**: Environment variables, no hardcoded secrets

## Deployment

### Development
```bash
docker-compose up -d
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

### Production (Future)
- Docker Compose for orchestration
- Nginx reverse proxy
- SSL/TLS certificates
- Environment-specific configurations
- Automated backups

## Technology Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Axios
- React Query

### Backend
- Python 3.11+
- FastAPI
- Prisma
- Pydantic
- python-jose (JWT)
- passlib (password hashing)

### Databases
- PostgreSQL 16
- Neo4j 5.15

### AI/ML
- LangChain
- LangGraph
- OpenAI API
- Anthropic API

### Infrastructure
- Docker
- Docker Compose
- GitHub Actions (CI/CD)

## Month 1 Status

✅ **Completed**:
- Project structure setup
- Docker Compose configuration
- Backend API with FastAPI
- User authentication system
- Project CRUD operations
- Frontend with Next.js
- Authentication pages (login/register)
- Dashboard layout
- Comprehensive documentation

⏳ **Pending** (Future Months):
- Prisma database integration
- Neo4j schema implementation
- Tool containers
- AI agent implementation
- Reconnaissance pipeline
- Vulnerability scanning
- Report generation

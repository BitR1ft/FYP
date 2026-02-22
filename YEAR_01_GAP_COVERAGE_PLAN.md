# AutoPenTest AI — Year 1 Gap Coverage: Day-by-Day Implementation Plan

> **Purpose**: Fill all identified gaps from GAP.md with a structured, day-by-day approach
> **Duration**: Flexible (time is not a constraint)
> **Task Density**: 3-4 actionable tasks per day
> **Focus**: Production-grade implementation with testing and documentation

---

## 📊 Overview

This plan systematically addresses all 11 phases identified in GAP.md:
- **Phase A**: Database Integration & Persistence (PostgreSQL + Prisma)
- **Phase B**: External Recon Tools Integration
- **Phase C**: Vulnerability Enrichment & Mapping
- **Phase D**: Graph Database Schema & Ingestion (Neo4j)
- **Phase E**: AI Agent Foundation & Streaming
- **Phase F**: MCP Tool Servers
- **Phase G**: Frontend (Next.js) UI
- **Phase H**: Observability & Security
- **Phase I**: Testing & QA
- **Phase J**: CI/CD & Releases
- **Phase K**: Documentation

**Total Estimated Days**: ~180 days (6 months at steady pace)

---

## 🎯 Phase A: Database Integration & Persistence (Days 1-20)

### Week 1: Schema Design & Setup (Days 1-7)

#### **Day 1: Prisma Schema Analysis**
- [ ] Review existing Prisma schema at `backend/prisma/schema.prisma`
- [ ] Document current models and identify missing models
- [ ] Create schema design document for User, Project, Task, Session models
- [ ] Define relationships between models

#### **Day 2: User & Auth Models**
- [ ] Extend Prisma User model with all required fields (email, password_hash, role, created_at, updated_at)
- [ ] Add Session model for JWT refresh tokens
- [ ] Create unique constraints and indexes
- [ ] Generate Prisma migration

#### **Day 3: Project Model Implementation**
- [ ] Design Project model with all fields (name, target, description, status, config, user_id)
- [ ] Add project status enum (draft, running, paused, completed, failed)
- [ ] Add relationships to User model
- [ ] Generate and test migration

#### **Day 4: Task Models (Recon, Scan, Probe)**
- [ ] Create Task base model with common fields (id, project_id, type, status, created_at, started_at, completed_at)
- [ ] Add ReconTask model for domain discovery results
- [ ] Add PortScanTask model for port scanning results
- [ ] Add HttpProbeTask model for HTTP probing results

#### **Day 5: Task Results & Metadata**
- [ ] Add TaskResult model for storing JSON outputs
- [ ] Add TaskLog model for execution logs
- [ ] Add TaskMetrics model for performance data
- [ ] Generate combined migration

#### **Day 6: Database Migration Testing**
- [ ] Apply all migrations to development database
- [ ] Test rollback functionality
- [ ] Verify all constraints and indexes are created
- [ ] Document migration commands

#### **Day 7: Seed Script Development**
- [ ] Create seed script for admin user
- [ ] Add sample project data
- [ ] Add sample task data for testing
- [ ] Test seed script execution

### Week 2: Repository Layer (Days 8-14)

#### **Day 8: Repository Pattern Setup**
- [ ] Create `backend/app/db/repositories/` directory structure
- [ ] Implement base repository class with common CRUD operations
- [ ] Set up async Prisma client singleton
- [ ] Add connection pooling configuration

#### **Day 9: User Repository**
- [ ] Implement `users_repo.py` with CRUD operations
- [ ] Add methods: create_user, get_by_id, get_by_email, update_user, delete_user
- [ ] Add password hashing integration
- [ ] Write unit tests for user repository

#### **Day 10: Project Repository**
- [ ] Implement `projects_repo.py` with CRUD operations
- [ ] Add methods: create, get_by_id, get_by_user, update, delete, list_with_filters
- [ ] Add pagination support
- [ ] Write unit tests for project repository

#### **Day 11: Task Repository**
- [ ] Implement `tasks_repo.py` for task management
- [ ] Add methods: create_task, get_by_id, get_by_project, update_status, store_result
- [ ] Add task filtering and sorting
- [ ] Write unit tests

#### **Day 12: Session Repository**
- [ ] Implement `sessions_repo.py` for JWT refresh tokens
- [ ] Add methods: create_session, get_by_token, revoke_session, cleanup_expired
- [ ] Add session validation logic
- [ ] Write unit tests

#### **Day 13: Service Layer Integration**
- [ ] Create service layer in `backend/app/services/`
- [ ] Implement `auth_service.py` using user and session repositories
- [ ] Implement `project_service.py` using project repository
- [ ] Add transaction support for complex operations

#### **Day 14: Background Job Integration**
- [ ] Update background job system to use task repository
- [ ] Replace in-memory task tracking with database
- [ ] Add job status updates to database
- [ ] Test background job persistence

### Week 3: API Refactoring (Days 15-20)

#### **Day 15: Auth Endpoints Refactoring**
- [ ] Refactor `/auth/register` to use user repository
- [ ] Refactor `/auth/login` to use user repository and session repository
- [ ] Update `/auth/me` endpoint
- [ ] Update `/auth/refresh` endpoint with session validation

#### **Day 16: Project CRUD Endpoints**
- [ ] Refactor `POST /projects` to use project repository
- [ ] Refactor `GET /projects` with pagination
- [ ] Refactor `GET /projects/{id}` endpoint
- [ ] Add filtering and sorting to list endpoint

#### **Day 17: Project Update & Delete**
- [ ] Refactor `PUT /projects/{id}` endpoint
- [ ] Refactor `DELETE /projects/{id}` with cascade
- [ ] Add project status update endpoints
- [ ] Test all CRUD operations

#### **Day 18: Health & Readiness Checks**
- [ ] Update `/health` endpoint to check database connection
- [ ] Add `/readiness` endpoint with dependency checks
- [ ] Implement startup event with database migration check
- [ ] Add database connection retry logic

#### **Day 19: Backup Strategy Implementation**
- [ ] Create `backup/` directory structure
- [ ] Write `pg_dump` backup script
- [ ] Implement daily backup cron job
- [ ] Add backup retention policy (7/30 days)

#### **Day 20: Testing & Documentation**
- [ ] Write integration tests for database-backed endpoints
- [ ] Verify 80%+ code coverage for DB layer
- [ ] Update API documentation
- [ ] Document database schema, migrations, and backup procedures

---

## 🔍 Phase B: External Recon Tools Integration (Days 21-50)

### Week 4: Tool Integration Framework (Days 21-27)

#### **Day 21: Canonical Schema Design**
- [ ] Define `ReconResult` schema with common fields
- [ ] Define `Endpoint` schema for discovered endpoints
- [ ] Define `Technology` schema for tech stack detection
- [ ] Define `Finding` schema for vulnerabilities

#### **Day 22: Tool Orchestrator Base Class**
- [ ] Create `backend/app/recon/orchestrators/base.py`
- [ ] Implement base orchestrator with common methods
- [ ] Add input validation and sanitization
- [ ] Add output normalization interface

#### **Day 23: Tool Container Setup**
- [ ] Update `docker/kali/Dockerfile` with tool versions
- [ ] Pin versions for Naabu, Nuclei, Katana, GAU, Kiterunner
- [ ] Add httpx, Wappalyzer, mmh3
- [ ] Test container build

#### **Day 24: Rate Limiting & Retry Logic**
- [ ] Implement rate limiter class with token bucket algorithm
- [ ] Add exponential backoff for retries
- [ ] Create retry decorator for tool execution
- [ ] Add configuration for rate limits per tool

#### **Day 25: Deduplication Pipeline**
- [ ] Create deduplication service
- [ ] Implement hash-based deduplication for endpoints
- [ ] Add fuzzy matching for similar findings
- [ ] Create confidence scoring system

#### **Day 26: Logging & Metrics**
- [ ] Add structured logging for tool execution
- [ ] Create metrics collection points (execution time, success rate, errors)
- [ ] Add tool-specific log formatters
- [ ] Set up log aggregation

#### **Day 27: Integration Testing Framework**
- [ ] Create test fixtures for tool outputs
- [ ] Set up mock tool execution for testing
- [ ] Create performance test harness
- [ ] Document testing approach

### Week 5: Port Scanning Tools (Days 28-34)

#### **Day 28: Naabu Integration - Setup**
- [x] Create `naabu_orchestrator.py`
- [x] Implement target validation (IP, CIDR, domain)
- [x] Add safe defaults (rate limiting, exclude private ranges)
- [x] Create Naabu configuration class

#### **Day 29: Naabu Integration - Execution**
- [x] Implement concurrent scanning logic
- [x] Add port range configuration
- [x] Implement output parsing (JSON format)
- [x] Add error handling and recovery

#### **Day 30: Naabu Integration - Testing**
- [x] Write unit tests for Naabu orchestrator
- [x] Create integration test with mock Naabu
- [x] Test with real Naabu against safe targets
- [x] Document Naabu usage and configuration

#### **Day 31: Port Scan Results Processing**
- [x] Create port scan result normalization
- [x] Implement service detection integration
- [x] Add port to graph database ingestion
- [x] Test end-to-end port scanning flow

#### **Day 32: Port Scan API Endpoints**
- [x] Create `POST /api/scans/ports` endpoint
- [x] Create `GET /api/scans/ports/{id}` status endpoint
- [x] Create `GET /api/scans/ports/{id}/results` endpoint
- [x] Add API documentation

#### **Day 33: Nmap Integration (Optional Enhancement)**
- [x] Create `nmap_orchestrator.py` for detailed scans
- [x] Implement service version detection
- [x] Add OS detection capability
- [x] Write tests and documentation

#### **Day 34: Port Scanning Documentation**
- [x] Document port scanning architecture
- [x] Add usage examples
- [x] Document safe defaults and rate limits
- [x] Create troubleshooting guide

### Week 6: Vulnerability Scanning (Days 35-41)

#### **Day 35: Nuclei Integration - Setup**
- [x] Create `nuclei_orchestrator.py`
- [x] Implement template management system
- [x] Add severity filtering (info, low, medium, high, critical)
- [x] Add tag-based template selection

#### **Day 36: Nuclei Integration - Execution**
- [x] Implement Nuclei execution with rate limiting
- [x] Add parallel target scanning
- [x] Implement output parsing (JSON format)
- [x] Add error handling

#### **Day 37: Nuclei Template Updates**
- [x] Create auto-update script for Nuclei templates
- [x] Implement scheduled template refresh
- [x] Add template versioning
- [x] Test update mechanism

#### **Day 38: Nuclei Results Processing**
- [x] Normalize Nuclei outputs to Finding schema
- [x] Implement severity mapping
- [x] Add CVE extraction from findings
- [x] Create deduplication logic

#### **Day 39: Nuclei API Integration**
- [x] Create `POST /api/scans/nuclei` endpoint
- [x] Add template filtering parameters
- [x] Create status and results endpoints
- [x] Test API endpoints

#### **Day 40: Interactsh Integration**
- [x] Integrate Interactsh for blind vulnerability detection
- [x] Create Interactsh client wrapper
- [x] Add OOB interaction tracking
- [x] Test with Nuclei OOB templates

#### **Day 41: Vulnerability Scanning Documentation**
- [x] Document Nuclei integration architecture
- [x] Add template management guide
- [x] Document severity filtering
- [x] Create usage examples

### Week 7: Web Crawling & URL Discovery (Days 42-48)

#### **Day 42: Katana Integration - Setup**
- [x] Create `katana_orchestrator.py`
- [x] Implement crawl configuration (depth, scope, filters)
- [x] Add JavaScript rendering option
- [x] Create output parser

#### **Day 43: Katana Integration - Execution**
- [x] Implement crawling with rate limiting
- [x] Add form detection and parameter extraction
- [x] Implement scope enforcement
- [x] Test crawling functionality

#### **Day 44: GAU Integration**
- [x] Create `gau_orchestrator.py`
- [x] Integrate 4 providers (Wayback, Common Crawl, OTX, URLScan)
- [x] Add provider selection and fallback
- [x] Implement result merging

#### **Day 45: Kiterunner Integration**
- [x] Create `kiterunner_orchestrator.py`
- [x] Implement API endpoint brute-forcing
- [x] Add wordlist management
- [x] Test API discovery

#### **Day 46: URL Discovery Merging**
- [x] Create URL deduplication pipeline
- [x] Merge results from Katana, GAU, Kiterunner
- [x] Add URL categorization (static, API, form, etc.)
- [x] Implement confidence scoring

#### **Day 47: Endpoint API Integration**
- [x] Create `POST /api/discovery/urls` endpoint
- [x] Add tool selection parameters
- [x] Create results endpoint with filtering
- [x] Test API endpoints

#### **Day 48: Web Crawling Documentation**
- [x] Document crawling architecture
- [x] Add tool comparison guide
- [x] Document URL categorization
- [x] Create usage examples

### Week 8: Technology Detection & Fingerprinting (Days 49-50)

#### **Day 49: Wappalyzer & httpx Integration**
- [x] Create `wappalyzer_orchestrator.py`
- [x] Integrate httpx for HTTP fingerprinting
- [x] Add TLS/JARM fingerprinting
- [x] Implement header analysis

#### **Day 50: Shodan Integration & Phase B Completion**
- [x] Create `shodan_orchestrator.py`
- [x] Implement Shodan API client with rate limiting
- [x] Add passive intelligence gathering
- [x] Complete Phase B testing and documentation

---

## 🔐 Phase C: Vulnerability Enrichment & Mapping (Days 51-65)

### Week 9: CVE Enrichment (Days 51-57)

#### **Day 51: Enrichment Service Design**
- [x] Design enrichment service architecture
- [x] Create `backend/app/services/enrichment/enrichment_service.py`
- [x] Define enrichment data models (EnrichedCVE, CVSSVector, ExploitInfo)
- [x] Set up caching strategy

#### **Day 52: NVD Integration**
- [x] Create NVD API client (`nvd_client.py`)
- [x] Implement CVE lookup by ID
- [x] Add CVSS score extraction
- [x] Implement rate limiting for NVD API

#### **Day 53: Vulners Integration**
- [x] Create Vulners API client (`vulners_client.py`)
- [x] Implement vulnerability search
- [x] Add exploit availability checking
- [x] Merge NVD and Vulners data

#### **Day 54: CVE Caching System**
- [x] Implement SQLite cache for CVE data (`cve_cache.py`)
- [x] Add cache expiration policy (30 days)
- [x] Create cache warming strategy
- [x] Test cache performance

#### **Day 55: CVE Enrichment Pipeline**
- [x] Create enrichment pipeline for findings
- [x] Add batch enrichment capability
- [x] Implement fallback strategies
- [x] Test enrichment accuracy

#### **Day 56: CVE API Endpoints**
- [x] Create `GET /api/cve/{id}` endpoint
- [x] Create `POST /api/enrich/findings` endpoint
- [x] Add batch enrichment endpoint
- [x] Test API endpoints

#### **Day 57: CVE Integration Testing**
- [x] Write integration tests for enrichment
- [x] Test with real CVE data
- [x] Verify CVSS scoring
- [x] Document enrichment service

### Week 10: CWE & CAPEC Mapping (Days 58-65)

#### **Day 58: CWE Database Setup**
- [x] Download CWE database (XML format parser)
- [x] Create CWE parser (`cwe_service.py`)
- [x] In-memory CWE data with built-in dataset + XML fallback
- [x] Create CWE lookup service

#### **Day 59: CAPEC Database Setup**
- [x] Download CAPEC database (XML format parser)
- [x] Create CAPEC parser (`capec_service.py`)
- [x] In-memory CAPEC data with built-in dataset + XML fallback
- [x] Create CAPEC lookup service

#### **Day 60: CWE-CAPEC Mapping**
- [x] Create mapping between CWE and CAPEC (`cwe_capec_mapper.py`)
- [x] Implement bidirectional relationship graph
- [x] Add attack pattern enrichment for Finding objects
- [x] Test mapping accuracy

#### **Day 61: Vulnerability → CWE Mapping**
- [x] Implement CWE extraction from CVE data (`vuln_cwe_mapper.py`)
- [x] Add CWE to vulnerability findings
- [x] Create vulnerability categorization (Injection/XSS/CSRF/SSRF/…)
- [x] Test CWE mapping

#### **Day 62: Risk Scoring Implementation**
- [x] Create risk scoring algorithm (`risk_scorer.py`)
- [x] Combine CVSS, exploitability, and exposure
- [x] Add severity normalization
- [x] Implement risk prioritization

#### **Day 63: Auto-Update Routines**
- [x] Create scheduled job for CVE updates (`update_scheduler.py`)
- [x] Add CWE/CAPEC refresh jobs
- [x] Implement Nuclei template updates
- [x] Add update audit logging

#### **Day 64: Enrichment API Endpoints**
- [x] Create filtered query endpoints (`enrichment_api.py`)
- [x] Add severity filtering
- [x] Add exploitability filtering
- [x] Implement search functionality

#### **Day 65: Phase C Testing & Documentation**
- [x] Write comprehensive tests for enrichment (`test_week9_cve_enrichment.py`, `test_week10_cwe_capec.py`)
- [x] Test scheduled updates
- [x] Document enrichment architecture
- [x] Create usage guide

---

## 📊 Phase D: Graph Database Schema & Ingestion (Days 66-85)

### Week 11: Graph Schema Design (Days 66-72)

#### **Day 66: Node Type Analysis**
- [x] Review current Neo4j schema
- [x] Document missing node types
- [x] Design 17+ node type schema
- [x] Create schema diagram

#### **Day 67: Core Node Types**
- [x] Implement Domain, Subdomain, IP, Port node types
- [x] Add constraints and indexes
- [x] Create node creation methods
- [x] Test node creation

#### **Day 68: Service & Technology Nodes**
- [x] Implement Service, BaseURL, Endpoint, Parameter nodes
- [x] Add Technology node with version info
- [x] Create relationship definitions
- [x] Test node relationships

#### **Day 69: Vulnerability & CVE Nodes**
- [x] Implement Vulnerability, CVE, CWE, CAPEC nodes
- [x] Add exploit and payload nodes
- [x] Create vulnerability chains
- [x] Test vulnerability relationships

#### **Day 70: Advanced Node Types**
- [x] Implement Credential, Session, Evidence nodes
- [x] Add Tool, Scan, Finding nodes
- [x] Create audit trail nodes (AuditEvent)
- [x] Test complete schema

#### **Day 71: Relationship Types**
- [x] Define 20+ relationship types
- [x] Add relationship properties
- [x] Implement relationship constraints
- [x] Create relationship methods

#### **Day 72: Schema Validation**
- [x] Create schema validation script
- [x] Test all node types and relationships
- [x] Verify constraints and indexes
- [x] Document complete schema

### Week 12: Ingestion Pipelines (Days 73-79)

#### **Day 73: Domain Discovery Ingestion**
- [x] Create ingestion function for domain discovery
- [x] Implement Domain → Subdomain → IP chain
- [x] Add batch ingestion capability
- [x] Test domain ingestion

#### **Day 74: Port Scan Ingestion**
- [x] Create ingestion for port scan results
- [x] Implement IP → Port → Service chain
- [x] Add service detection ingestion
- [x] Test port scan ingestion

#### **Day 75: HTTP Probe Ingestion**
- [x] Create ingestion for HTTP probing
- [x] Implement Endpoint → Technology chain
- [x] Add response metadata ingestion
- [x] Test HTTP probe ingestion

#### **Day 76: Resource Enumeration Ingestion**
- [x] Create ingestion for resource discovery
- [x] Implement Endpoint → Parameter chain
- [x] Add form and API endpoint ingestion
- [x] Test resource ingestion

#### **Day 77: Vulnerability Scan Ingestion**
- [x] Create ingestion for vulnerability findings
- [x] Implement Technology → Vulnerability → CVE chain
- [x] Add CWE/CAPEC relationship creation
- [x] Test vulnerability ingestion

#### **Day 78: MITRE ATT&CK Ingestion**
- [x] Create ingestion for MITRE techniques
- [x] Implement Vulnerability → CAPEC → Technique chain
- [x] Add tactic and technique nodes
- [x] Test MITRE ingestion

#### **Day 79: Complete Pipeline Testing**
- [x] Test end-to-end ingestion flow
- [x] Verify all relationships created
- [x] Test with sample project data
- [x] Document ingestion pipeline

### Week 13: Multi-tenancy & Queries (Days 80-85)

#### **Day 80: Multi-tenancy Implementation**
- [x] Add user_id and project_id to all nodes
- [x] Create tenant isolation queries
- [x] Implement access control checks
- [x] Test tenant isolation

#### **Day 81: Attack Surface Queries**
- [x] Create attack surface overview query
- [x] Implement exposed services query
- [x] Add technology inventory query
- [x] Test query performance

#### **Day 82: Vulnerability Queries**
- [x] Create vulnerability by severity query
- [x] Implement exploitable vulnerability query
- [x] Add CVE chain traversal queries
- [x] Test vulnerability queries

#### **Day 83: Path Finding Queries**
- [x] Implement attack path discovery
- [x] Create shortest path to vulnerability
- [x] Add critical path identification
- [x] Test path finding

#### **Day 84: Graph Stats Endpoints**
- [x] Create `/api/graph/stats` endpoint
- [x] Implement node count by type
- [x] Add relationship statistics
- [x] Create graph health metrics

#### **Day 85: Phase D Testing & Documentation**
- [x] Write comprehensive graph tests
- [x] Test with large datasets
- [x] Document graph schema and queries
- [x] Create usage examples

---

## 🤖 Phase E: AI Agent Foundation & Streaming (Days 86-105)

### Week 14: Agent Architecture (Days 86-92)

#### **Day 86: LangGraph Setup**
- [x] Set up LangGraph environment
- [x] Create agent graph structure
- [x] Define agent phases (recon, vuln scan, exploit, post-exploit)
- [x] Create phase transition logic

#### **Day 87: System Prompts**
- [x] Create system prompts per phase
- [x] Add chain-of-thought instructions
- [x] Implement context-aware prompting
- [x] Test prompt effectiveness

#### **Day 88: MemorySaver Implementation**
- [x] Implement MemorySaver for state persistence
- [x] Add checkpointing logic
- [x] Create state recovery mechanism
- [x] Test state persistence

#### **Day 89: Tool Interface Framework**
- [x] Create tool interface base class
- [x] Define tool input/output schemas
- [x] Implement tool registration system
- [x] Add tool validation

#### **Day 90: ReAct Pattern Implementation**
- [x] Implement ReAct reasoning loop
- [x] Add thought-action-observation cycle
- [x] Create action validation
- [x] Test ReAct flow

#### **Day 91: Agent Configuration**
- [x] Create agent configuration system
- [x] Add phase-specific configurations
- [x] Implement tool availability per phase
- [x] Test configuration loading

#### **Day 92: Agent Testing Framework**
- [x] Create agent testing utilities
- [x] Add mock LLM for testing
- [x] Create test scenarios
- [x] Test agent initialization

### Week 15: Tool Adapters (Days 93-99)

#### **Day 93: Recon Tool Adapter**
- [x] Create recon tool adapter
- [x] Implement domain discovery tool
- [x] Add port scanning tool
- [x] Test recon tools

#### **Day 94: HTTP Probe Tool Adapter**
- [x] Create HTTP probing tool adapter
- [x] Implement technology detection tool
- [x] Add endpoint enumeration tool
- [x] Test HTTP tools

#### **Day 95: Nuclei Tool Adapter**
- [x] Create Nuclei tool adapter
- [x] Implement template selection logic
- [x] Add vulnerability scanning tool
- [x] Test Nuclei integration

#### **Day 96: Graph Query Tool Adapter**
- [x] Create graph query tool adapter
- [x] Implement attack surface query tool
- [x] Add vulnerability lookup tool
- [x] Test graph tools

#### **Day 97: Web Search Tool Adapter**
- [x] Create web search tool adapter (Tavily)
- [x] Implement exploit search
- [x] Add CVE information lookup
- [x] Test web search

#### **Day 98: Tool Error Handling**
- [x] Implement tool-specific error recovery
- [x] Add retry logic for failed tools
- [x] Create error reporting
- [x] Test error scenarios

#### **Day 99: Tool Documentation**
- [x] Document all tool adapters
- [x] Create tool usage examples
- [x] Add tool limitations and safety notes
- [x] Create troubleshooting guide

### Week 16: Safety & Streaming (Days 100-105)

#### **Day 100: Approval Workflow**
- [x] Implement approval gate system
- [x] Add dangerous operation classification
- [x] Create approval request mechanism
- [x] Test approval flow

#### **Day 101: Stop/Resume Functionality**
- [x] Implement agent stop mechanism
- [x] Add state saving on stop
- [x] Create resume from checkpoint
- [x] Test stop/resume

#### **Day 102: SSE Streaming Implementation**
- [x] Create SSE endpoint for agent streaming
- [x] Implement event formatting
- [x] Add progress events
- [x] Test SSE streaming

#### **Day 103: WebSocket Streaming**
- [x] Create WebSocket endpoint for bidirectional communication
- [x] Implement approval requests via WebSocket
- [x] Add real-time event streaming
- [x] Test WebSocket connection

#### **Day 104: Session Management**
- [x] Implement agent session persistence
- [x] Add session ID management
- [x] Create session cleanup
- [x] Test session handling

#### **Day 105: Audit Logging**
- [x] Create comprehensive audit logging
- [x] Log all agent actions and decisions
- [x] Add tool execution logs
- [x] Test audit trail completeness

---

## 🔌 Phase F: MCP Tool Servers (Days 106-120)

### Week 17: MCP Protocol Implementation (Days 106-112)

#### **Day 106: MCP Specification Study**
- [ ] Study MCP protocol specification
- [ ] Design MCP server architecture
- [ ] Create protocol compliance checklist
- [ ] Document MCP requirements

#### **Day 107: MCP Server Skeleton**
- [ ] Create MCP server base class
- [ ] Implement protocol message handling
- [ ] Add request/response validation
- [ ] Test basic server

#### **Day 108: MCP Tool Registration**
- [ ] Implement tool registration system
- [ ] Create tool capability declaration
- [ ] Add tool metadata
- [ ] Test tool discovery

#### **Day 109: MCP Request Handling**
- [ ] Implement request routing
- [ ] Add parameter validation
- [ ] Create response formatting
- [ ] Test request handling

#### **Day 110: MCP Error Handling**
- [ ] Implement standardized error responses
- [ ] Add error codes and messages
- [ ] Create error recovery
- [ ] Test error scenarios

#### **Day 111: MCP Security**
- [ ] Implement authentication for MCP servers
- [ ] Add authorization checks
- [ ] Create rate limiting
- [ ] Test security controls

#### **Day 112: MCP Testing Framework**
- [ ] Create MCP server testing utilities
- [ ] Add protocol compliance tests
- [ ] Create load testing tools
- [ ] Test server performance

### Week 18: Tool Server Implementation (Days 113-120)

#### **Day 113: Naabu MCP Server**
- [ ] Create Naabu MCP server
- [ ] Implement port scanning tools
- [ ] Add configuration options
- [ ] Test Naabu server

#### **Day 114: Nuclei MCP Server**
- [ ] Create Nuclei MCP server
- [ ] Implement vulnerability scanning tools
- [ ] Add template management
- [ ] Test Nuclei server

#### **Day 115: Curl MCP Server**
- [ ] Create Curl MCP server
- [ ] Implement HTTP request tools
- [ ] Add header manipulation
- [ ] Test Curl server

#### **Day 116: Metasploit MCP Server**
- [ ] Create Metasploit MCP server
- [ ] Implement exploit tools
- [ ] Add payload generation
- [ ] Test Metasploit server

#### **Day 117: Query Graph MCP Server**
- [ ] Create Neo4j query MCP server
- [ ] Implement graph query tools
- [ ] Add attack path finding
- [ ] Test graph server

#### **Day 118: Web Search MCP Server**
- [ ] Create web search MCP server (Tavily)
- [ ] Implement search tools
- [ ] Add result filtering
- [ ] Test search server

#### **Day 119: Phase Restriction Implementation**
- [ ] Add phase-based tool access control
- [ ] Implement RBAC for tools
- [ ] Create permission validation
- [ ] Test access control

#### **Day 120: Phase F Testing & Documentation**
- [ ] Write comprehensive MCP tests
- [ ] Test all tool servers
- [ ] Document MCP architecture
- [ ] Create usage guide

---

## 🎨 Phase G: Frontend (Next.js) UI (Days 121-145)

### Week 19: Authentication UI (Days 121-127)

#### **Day 121: Auth Page Design**
- [ ] Design login and register pages
- [ ] Create wireframes and mockups
- [ ] Review UI/UX patterns
- [ ] Document design decisions

#### **Day 122: Login Page Implementation**
- [ ] Create login page component
- [ ] Implement form validation with Zod
- [ ] Add error handling
- [ ] Test login flow

#### **Day 123: Register Page Implementation**
- [ ] Create register page component
- [ ] Implement password strength validation
- [ ] Add email verification UI
- [ ] Test registration flow

#### **Day 124: Auth State Management**
- [ ] Implement auth context/store
- [ ] Add token management
- [ ] Create refresh token logic
- [ ] Test auth persistence

#### **Day 125: Protected Routes**
- [ ] Create route protection wrapper
- [ ] Implement redirect logic
- [ ] Add loading states
- [ ] Test route protection

#### **Day 126: User Profile Page**
- [ ] Create user profile component
- [ ] Implement profile editing
- [ ] Add password change functionality
- [ ] Test profile updates

#### **Day 127: Auth Integration Testing**
- [ ] Write E2E tests for authentication
- [ ] Test login/logout flows
- [ ] Test token refresh
- [ ] Document auth implementation

### Week 20: Project Management UI (Days 128-134)

#### **Day 128: Project List Page**
- [ ] Create project list component
- [ ] Implement filtering and sorting
- [ ] Add pagination
- [ ] Test list functionality

#### **Day 129: Project Card Component**
- [ ] Create project card design
- [ ] Add status indicators
- [ ] Implement action buttons
- [ ] Test card interactions

#### **Day 130: Project Detail Page**
- [ ] Create project detail component
- [ ] Display project information
- [ ] Add status timeline
- [ ] Test detail view

#### **Day 131: Project Creation - Step 1**
- [ ] Create multi-step form wizard
- [ ] Implement basic info step
- [ ] Add form validation
- [ ] Test step navigation

#### **Day 132: Project Creation - Step 2**
- [ ] Create target configuration step
- [ ] Implement scope definition
- [ ] Add target validation
- [ ] Test configuration

#### **Day 133: Project Creation - Step 3**
- [ ] Create tool selection step
- [ ] Implement tool configuration
- [ ] Add parameter management
- [ ] Test tool selection

#### **Day 134: Project Creation - Finalization**
- [ ] Create review and submit step
- [ ] Implement draft saving
- [ ] Add project creation API integration
- [ ] Test complete flow

### Week 21: Advanced Project Form (Days 135-141)

#### **Day 135: Form State Management**
- [ ] Implement form state with React Hook Form
- [ ] Add field validation
- [ ] Create error handling
- [ ] Test form state

#### **Day 136: 180+ Parameter Form - Part 1**
- [ ] Design parameter grouping
- [ ] Create accordion layout
- [ ] Implement first 60 parameters
- [ ] Test parameter inputs

#### **Day 137: 180+ Parameter Form - Part 2**
- [ ] Implement next 60 parameters
- [ ] Add conditional field display
- [ ] Create field dependencies
- [ ] Test parameter logic

#### **Day 138: 180+ Parameter Form - Part 3**
- [ ] Implement final 60+ parameters
- [ ] Add advanced configurations
- [ ] Create parameter presets
- [ ] Test complete form

#### **Day 139: Form Validation & Accessibility**
- [ ] Add comprehensive validation
- [ ] Implement ARIA labels
- [ ] Add keyboard navigation
- [ ] Test accessibility

#### **Day 140: Form Auto-save**
- [ ] Implement draft auto-save
- [ ] Add save indicators
- [ ] Create restore from draft
- [ ] Test auto-save functionality

#### **Day 141: Project Edit Functionality**
- [ ] Create project edit page
- [ ] Implement update logic
- [ ] Add conflict resolution
- [ ] Test project updates

### Week 22: Graph Visualization (Days 142-145)

#### **Day 142: 2D Graph Setup**
- [ ] Set up react-force-graph-2d
- [ ] Create graph container component
- [ ] Implement basic rendering
- [ ] Test graph initialization

#### **Day 143: Graph Interactions**
- [ ] Implement node click/hover
- [ ] Add zoom and pan controls
- [ ] Create node highlighting
- [ ] Test interactions

#### **Day 144: 3D Graph Implementation**
- [ ] Set up react-force-graph-3d
- [ ] Create 3D visualization
- [ ] Add camera controls
- [ ] Test 3D rendering

#### **Day 145: Node Inspector & Filters**
- [ ] Create node inspector panel
- [ ] Implement node type filters
- [ ] Add relationship filters
- [ ] Test filtering

### Week 23: Real-time Updates & Polish (Days 146-150)

#### **Day 146: SSE Client Implementation**
- [ ] Create SSE client utility
- [ ] Implement event handling
- [ ] Add reconnection logic
- [ ] Test SSE connection

#### **Day 147: WebSocket Client**
- [ ] Create WebSocket client utility
- [ ] Implement bidirectional messaging
- [ ] Add connection management
- [ ] Test WebSocket

#### **Day 148: Real-time Progress Updates**
- [ ] Integrate progress events
- [ ] Create progress indicators
- [ ] Add toast notifications
- [ ] Test real-time updates

#### **Day 149: Graph Export Functionality**
- [ ] Implement PNG export
- [ ] Add JSON export
- [ ] Create GEXF export
- [ ] Test export formats

#### **Day 150: Responsive Design & Dark Mode**
- [ ] Implement responsive breakpoints
- [ ] Add mobile optimizations
- [ ] Enhance dark mode support
- [ ] Test across devices

---

## 📈 Phase H: Observability & Security (Days 151-165)

### Week 24: Logging & Metrics (Days 151-157)

#### **Day 151: Structured Logging**
- [ ] Implement JSON logging format
- [ ] Add correlation IDs to requests
- [ ] Create log level configuration
- [ ] Test logging output

#### **Day 152: Logging Middleware**
- [ ] Create logging middleware for FastAPI
- [ ] Add request/response logging
- [ ] Implement sampling for high-volume endpoints
- [ ] Test middleware

#### **Day 153: Prometheus Metrics**
- [ ] Set up Prometheus exporter
- [ ] Add request latency metrics
- [ ] Create error rate metrics
- [ ] Test metric collection

#### **Day 154: Custom Metrics**
- [ ] Add tool execution metrics
- [ ] Create job duration metrics
- [ ] Implement queue length metrics
- [ ] Test custom metrics

#### **Day 155: Grafana Dashboards - Part 1**
- [ ] Set up Grafana
- [ ] Create API metrics dashboard
- [ ] Add system health dashboard
- [ ] Test dashboard rendering

#### **Day 156: Grafana Dashboards - Part 2**
- [ ] Create tool execution dashboard
- [ ] Add job performance dashboard
- [ ] Implement alerting dashboard
- [ ] Test all dashboards

#### **Day 157: OpenTelemetry Tracing**
- [ ] Set up OpenTelemetry
- [ ] Instrument FastAPI app
- [ ] Add trace context propagation
- [ ] Test distributed tracing

### Week 25: Security Hardening (Days 158-165)

#### **Day 158: Secrets Management**
- [ ] Implement secrets loading from environment
- [ ] Add secrets rotation support
- [ ] Create secrets validation
- [ ] Test secrets management

#### **Day 159: RBAC Implementation**
- [ ] Define user roles (admin, analyst, viewer)
- [ ] Implement role-based permissions
- [ ] Add role middleware
- [ ] Test RBAC

#### **Day 160: Audit Logging**
- [ ] Create audit log system
- [ ] Log sensitive operations
- [ ] Implement audit log retention
- [ ] Test audit logs

#### **Day 161: Rate Limiting**
- [ ] Implement per-user rate limiting
- [ ] Add per-project rate limits
- [ ] Create rate limit middleware
- [ ] Test rate limiting

#### **Day 162: CORS & WAF**
- [ ] Configure CORS properly
- [ ] Add basic WAF rules
- [ ] Implement request sanitization
- [ ] Test security headers

#### **Day 163: Dependency Scanning**
- [ ] Set up Dependabot
- [ ] Configure Snyk scanning
- [ ] Create dependency update policy
- [ ] Test scanning

#### **Day 164: Alert Configuration**
- [ ] Configure alerting rules
- [ ] Set up Slack integration
- [ ] Add email alerting
- [ ] Test alert delivery

#### **Day 165: Phase H Testing & Documentation**
- [ ] Test observability stack
- [ ] Verify security controls
- [ ] Document monitoring setup
- [ ] Create runbooks

---

## 🧪 Phase I: Testing & QA (Days 166-180)

### Week 26: Backend Testing (Days 166-172)

#### **Day 166: Unit Test Expansion**
- [ ] Expand unit tests for repositories
- [ ] Add tests for services
- [ ] Test utility functions
- [ ] Achieve 80%+ coverage

#### **Day 167: Integration Tests - Auth**
- [ ] Write integration tests for authentication
- [ ] Test token lifecycle
- [ ] Test session management
- [ ] Verify error handling

#### **Day 168: Integration Tests - Projects**
- [ ] Write integration tests for project CRUD
- [ ] Test project workflows
- [ ] Test concurrent operations
- [ ] Verify data consistency

#### **Day 169: Integration Tests - Orchestrators**
- [ ] Write tests for tool orchestrators
- [ ] Test error handling
- [ ] Test rate limiting
- [ ] Verify output normalization

#### **Day 170: Integration Tests - Graph**
- [ ] Write tests for graph ingestion
- [ ] Test query functions
- [ ] Test multi-tenancy
- [ ] Verify relationship integrity

#### **Day 171: Contract Tests - MCP**
- [ ] Write contract tests for MCP servers
- [ ] Test protocol compliance
- [ ] Verify tool interfaces
- [ ] Test error responses

#### **Day 172: Contract Tests - Agent**
- [ ] Write tests for agent tools
- [ ] Test tool execution
- [ ] Verify approval workflow
- [ ] Test state management

### Week 27: Frontend & E2E Testing (Days 173-180)

#### **Day 173: Frontend Unit Tests**
- [ ] Expand component unit tests
- [ ] Test custom hooks
- [ ] Test utility functions
- [ ] Achieve 70%+ coverage

#### **Day 174: E2E Tests - Authentication**
- [ ] Write E2E test for login
- [ ] Test registration flow
- [ ] Test password reset
- [ ] Test session expiry

#### **Day 175: E2E Tests - Projects**
- [ ] Write E2E test for project creation
- [ ] Test project editing
- [ ] Test project deletion
- [ ] Test project listing

#### **Day 176: E2E Tests - Recon**
- [ ] Write E2E test for recon workflow
- [ ] Test tool execution
- [ ] Test result viewing
- [ ] Test graph updates

#### **Day 177: E2E Tests - Graph**
- [ ] Write E2E test for graph viewing
- [ ] Test graph interactions
- [ ] Test filtering
- [ ] Test export functionality

#### **Day 178: Performance Testing**
- [ ] Create performance test suite
- [ ] Test API throughput
- [ ] Test concurrent users
- [ ] Document baselines

#### **Day 179: Chaos Testing**
- [ ] Test database failure scenarios
- [ ] Test Neo4j failure recovery
- [ ] Test tool failure handling
- [ ] Verify graceful degradation

#### **Day 180: Phase I Completion**
- [ ] Review all test results
- [ ] Verify coverage thresholds met
- [ ] Document test strategy
- [ ] Create testing guide

---

## 🚀 Phase J: CI/CD & Releases (Days 181-195)

### Week 28: CI Pipeline (Days 181-187)

#### **Day 181: GitHub Actions Setup**
- [ ] Create workflow directory structure
- [ ] Set up workflow triggers
- [ ] Configure workflow permissions
- [ ] Test workflow execution

#### **Day 182: Backend CI Workflow**
- [ ] Create backend lint job
- [ ] Add backend test job
- [ ] Implement code coverage reporting
- [ ] Test backend CI

#### **Day 183: Frontend CI Workflow**
- [ ] Create frontend lint job
- [ ] Add frontend test job
- [ ] Implement coverage reporting
- [ ] Test frontend CI

#### **Day 184: Security Scanning**
- [ ] Add dependency scanning job
- [ ] Implement SAST scanning
- [ ] Add container scanning
- [ ] Test security checks

#### **Day 185: Docker Build Pipeline**
- [ ] Create multi-stage Dockerfile optimization
- [ ] Implement layer caching
- [ ] Add SBOM generation
- [ ] Test Docker builds

#### **Day 186: Integration Tests in CI**
- [ ] Set up test database in CI
- [ ] Add Neo4j for testing
- [ ] Run integration tests
- [ ] Test CI integration

#### **Day 187: CI Documentation**
- [ ] Document CI workflows
- [ ] Create troubleshooting guide
- [ ] Document CI/CD best practices
- [ ] Create contribution guide

### Week 29: CD & Release (Days 188-195)

#### **Day 188: Staging Environment**
- [ ] Set up staging environment configuration
- [ ] Create staging deployment workflow
- [ ] Implement smoke tests
- [ ] Test staging deployment

#### **Day 189: Production Environment**
- [ ] Set up production environment configuration
- [ ] Create production deployment workflow
- [ ] Add deployment approval gates
- [ ] Document deployment process

#### **Day 190: Blue/Green Deployment**
- [ ] Implement blue/green deployment strategy
- [ ] Create traffic switching logic
- [ ] Add health checks
- [ ] Test zero-downtime deployment

#### **Day 191: Rollback Procedures**
- [ ] Create rollback workflow
- [ ] Implement database rollback strategy
- [ ] Add rollback verification
- [ ] Test rollback procedures

#### **Day 192: Release Automation**
- [ ] Create release workflow
- [ ] Implement version tagging
- [ ] Add changelog generation
- [ ] Test release process

#### **Day 193: Artifact Management**
- [ ] Set up artifact registry
- [ ] Implement artifact versioning
- [ ] Add artifact retention policy
- [ ] Test artifact storage

#### **Day 194: Secrets Management in CI/CD**
- [ ] Set up GitHub Secrets
- [ ] Implement secret rotation
- [ ] Add secret scanning
- [ ] Test secret management

#### **Day 195: Phase J Completion**
- [ ] Test complete CI/CD pipeline
- [ ] Verify all deployments work
- [ ] Document release process
- [ ] Create operations runbook

---

## 📚 Phase K: Documentation (Days 196-210)

### Week 30: API & Technical Docs (Days 196-202)

#### **Day 196: OpenAPI Documentation**
- [ ] Update OpenAPI schema
- [ ] Add detailed endpoint descriptions
- [ ] Include request/response examples
- [ ] Test API docs generation

#### **Day 197: Module Documentation**
- [ ] Add docstrings to all modules
- [ ] Create module overview docs
- [ ] Document key classes and functions
- [ ] Generate API reference

#### **Day 198: Database Documentation**
- [ ] Document database schema
- [ ] Create ER diagrams
- [ ] Document migrations
- [ ] Add seeding guide

#### **Day 199: Graph Schema Documentation**
- [ ] Document Neo4j schema
- [ ] Create graph diagrams
- [ ] Document queries
- [ ] Add ingestion guide

#### **Day 200: Agent Documentation**
- [ ] Document agent architecture
- [ ] Create agent flow diagrams
- [ ] Document tool interfaces
- [ ] Add safety model documentation

#### **Day 201: MCP Documentation**
- [ ] Document MCP protocol usage
- [ ] Create tool server guides
- [ ] Document tool capabilities
- [ ] Add troubleshooting guide

#### **Day 202: Architecture Documentation**
- [ ] Create system architecture diagrams
- [ ] Document data flow
- [ ] Add component interaction diagrams
- [ ] Document deployment architecture

### Week 31: Operational & User Docs (Days 203-210)

#### **Day 203: Installation Guide**
- [ ] Create comprehensive installation guide
- [ ] Document prerequisites
- [ ] Add troubleshooting section
- [ ] Test installation steps

#### **Day 204: Configuration Guide**
- [ ] Document all configuration options
- [ ] Create configuration examples
- [ ] Add environment variable reference
- [ ] Document best practices

#### **Day 205: Operations Runbook**
- [ ] Create operations checklist
- [ ] Document backup procedures
- [ ] Add disaster recovery guide
- [ ] Document monitoring setup

#### **Day 206: Migration Playbook**
- [ ] Document database migrations
- [ ] Create upgrade procedures
- [ ] Add rollback instructions
- [ ] Document breaking changes

#### **Day 207: User Manual Updates**
- [ ] Update user manual with new features
- [ ] Add screenshots and examples
- [ ] Create video tutorials
- [ ] Test all user flows

#### **Day 208: Developer Guide**
- [ ] Create development setup guide
- [ ] Document code standards
- [ ] Add contribution guidelines
- [ ] Create pull request template

#### **Day 209: Threat Model**
- [ ] Document security architecture
- [ ] Create threat model
- [ ] Document mitigations
- [ ] Add security best practices

#### **Day 210: Final Documentation Review**
- [ ] Review all documentation
- [ ] Fix broken links
- [ ] Verify examples work
- [ ] Publish documentation

---

## ✅ Final Verification & Acceptance (Days 211-215)

### **Day 211: Complete System Testing**
- [ ] Run complete test suite
- [ ] Verify all acceptance criteria met
- [ ] Test end-to-end workflows
- [ ] Document test results

### **Day 212: Performance Verification**
- [ ] Run performance benchmarks
- [ ] Verify resource usage
- [ ] Test scalability
- [ ] Document performance metrics

### **Day 213: Security Audit**
- [ ] Run security scans
- [ ] Review audit logs
- [ ] Verify RBAC implementation
- [ ] Document security posture

### **Day 214: Documentation Verification**
- [ ] Verify all documentation complete
- [ ] Test documentation examples
- [ ] Review with stakeholders
- [ ] Publish final documentation

### **Day 215: Project Completion**
- [ ] Review all phases completed
- [ ] Verify all gaps filled
- [ ] Create completion report
- [ ] Celebrate success! 🎉

---

## 📊 Progress Tracking

### Phase Completion Checklist
- [ ] Phase A: Database Integration & Persistence (Days 1-20)
- [ ] Phase B: External Recon Tools Integration (Days 21-50)
- [ ] Phase C: Vulnerability Enrichment & Mapping (Days 51-65)
- [ ] Phase D: Graph Database Schema & Ingestion (Days 66-85)
- [ ] Phase E: AI Agent Foundation & Streaming (Days 86-105)
- [ ] Phase F: MCP Tool Servers (Days 106-120)
- [ ] Phase G: Frontend (Next.js) UI (Days 121-150)
- [ ] Phase H: Observability & Security (Days 151-165)
- [ ] Phase I: Testing & QA (Days 166-180)
- [ ] Phase J: CI/CD & Releases (Days 181-195)
- [ ] Phase K: Documentation (Days 196-210)
- [ ] Final Verification (Days 211-215)

### Success Metrics
- [ ] All 346 tasks completed
- [ ] All acceptance criteria met
- [ ] Test coverage ≥80% backend, ≥70% frontend
- [ ] All documentation complete and verified
- [ ] System passes security audit
- [ ] Performance benchmarks met

---

## 🎯 Key Principles

1. **Quality Over Speed**: Take time to do it right
2. **Test Everything**: Write tests before marking tasks complete
3. **Document As You Go**: Don't leave documentation to the end
4. **Review Regularly**: Review progress weekly
5. **Security First**: Security considerations in every task
6. **User-Centric**: Keep end-user experience in mind

---

## 📝 Daily Task Execution Guidelines

For each day:
1. **Morning**: Review day's tasks and prepare environment
2. **Execution**: Complete 3-4 tasks with testing
3. **Documentation**: Document changes and decisions
4. **Review**: Test completed work and update progress
5. **Commit**: Commit code with descriptive messages

---

## 🚨 Important Notes

- **Flexibility**: Adjust daily tasks as needed based on complexity
- **Dependencies**: Some tasks depend on previous completion
- **Parallel Work**: Some phases can be worked on in parallel
- **Breaks**: Take breaks between phases for review and planning
- **Help**: Don't hesitate to ask for help when stuck

---

**Good luck with filling all the gaps! 🚀**

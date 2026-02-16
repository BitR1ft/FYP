# AutoPenTest AI

An agentic, fully-automated penetration testing framework that autonomously executes the entire penetration testing kill chain.

## 🎯 Project Overview

AutoPenTest AI is a Linux-based, AI-powered offensive security framework that, given a single target, autonomously executes:
- **Reconnaissance**: Multi-phase discovery, web/API detection, technology fingerprinting
- **Exploitation**: CVE-based attacks, web vulnerabilities, credential attacks
- **Privilege Escalation**: Automated user and root flag acquisition (Linux/Windows)
- **Post-Exploitation**: Enumeration, credential harvesting, evidence collection
- **Report Generation**: Professional PDF/HTML reports with remediation guidance

### Target Success Rates
- HTB Easy: 100%
- HTB Medium: ≥95%
- HTB Hard: 90-95%

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                          │
│           (TypeScript, Tailwind CSS, shadcn/ui)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                    WebSocket/SSE (Real-time)
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                  (Python, JWT Auth, REST API)                    │
└─────────────────────────────────────────────────────────────────┘
                    │                         │
        ┌───────────┴──────────┐    ┌────────┴─────────┐
        │                      │    │                  │
    PostgreSQL              Neo4j         AI Agent      │
  (Configuration)    (Attack Graph)   (LangGraph)      │
                                                        │
                                          ┌─────────────┴──────────┐
                                          │    Kali Tool Sandbox   │
                                          │  (Nmap, Nuclei, etc.)  │
                                          └────────────────────────┘
```

## 📚 Technology Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: TanStack Query
- **Visualization**: react-force-graph (2D/3D)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: Prisma (PostgreSQL)
- **Authentication**: JWT
- **Real-time**: WebSocket/SSE

### Databases
- **PostgreSQL**: Configuration, users, projects, settings
- **Neo4j**: Attack surface graph, relationships, findings

### AI & Tools
- **Agent Framework**: LangGraph/LangChain
- **LLM Providers**: OpenAI/Anthropic
- **Security Tools**: Nmap, Naabu, Nuclei, SQLMap, Metasploit, LinPEAS/WinPEAS, etc.

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest (Python), Jest (TypeScript)

## 🚀 Getting Started

### Prerequisites
- Docker Desktop (or Docker + Docker Compose)
- Node.js 22+
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/BitR1ft/FYP.git
cd FYP
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the services with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📖 Documentation

- [Project Proposal](FYP%20-%20Proposal.md)
- [Year 1 Development Plan](FYP%20-%20YEAR%2001.md)
- [Year 2 Development Plan](FYP%20-%20YEAR%2002.md)
- [API Documentation](http://localhost:8000/docs) (when backend is running)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📋 Project Status

**Current Phase**: Month 7 - Vulnerability Scanning Complete ✅

**Completed Months**:
- ✅ Month 1: Foundation & Environment Setup
- ✅ Month 2: Core Infrastructure  
- ✅ Month 3: Reconnaissance Pipeline - Phase 1 (Domain Discovery)
- ✅ Month 4: Reconnaissance Pipeline - Phase 2 (Port Scanning)
- ✅ Month 5: Reconnaissance Pipeline - Phase 3 (HTTP Probing & Technology Detection)
- ✅ Month 6: Reconnaissance Pipeline - Phase 4 (Resource Enumeration)
- ✅ Month 7: Vulnerability Scanning (Nuclei Integration, CVE Enrichment & MITRE Mapping)

**Next**: Month 8 - Neo4j Graph Database (Schema Design & Data Ingestion)

See [Year 1 Plan](FYP%20-%20YEAR%2001.md) for detailed progress tracking.

## 🔒 Security & Ethics

This framework is designed for authorized penetration testing only. Key safeguards:
- Strict scope enforcement
- Approval gates for destructive actions
- Complete audit logging
- Legal disclaimers and responsible use policy

**⚠️ Warning**: Unauthorized use of this tool against systems you don't own or have explicit permission to test is illegal and unethical.

## 📝 License

[Add your license here]

## 👨‍💻 Author

**Muhammad Adeel Haider**
- Program: BSCYS-F24 A
- Supervisor: Sir Galib

## 🙏 Acknowledgments

- Inspired by RedAmon framework
- Built on top of industry-standard security tools
- Leveraging modern AI capabilities with LangGraph

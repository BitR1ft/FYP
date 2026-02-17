# Month 11: MCP Tool Servers Documentation

## Overview

Month 11 implementation adds Model Context Protocol (MCP) tool servers for integrating security tools with the AI agent. This allows the agent to interact with various security tools through a standardized JSON-RPC interface.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Agent (LangGraph)                        │
│                    with Tool Registry                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    MCP Client (JSON-RPC)
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼─────┐      ┌─────▼──────┐      ┌────▼─────┐
    │  Naabu   │      │   Curl     │      │  Nuclei  │
    │  Server  │      │   Server   │      │  Server  │
    │ Port 8000│      │ Port 8001  │      │ Port 8002│
    └──────────┘      └────────────┘      └──────────┘
         │
    ┌────▼─────────┐
    │ Metasploit   │
    │   Server     │
    │  Port 8003   │
    └──────────────┘
```

## MCP Servers

### 1. Naabu Server (Port 8000)

**Purpose**: Fast port scanning

**Tools**:
- `execute_naabu`: Execute port scan on target

**Parameters**:
- `target` (required): IP address, CIDR, or hostname
- `ports` (optional): Port range (e.g., "1-1000", "top-100")
- `rate` (optional): Packets per second (default: 1000)
- `timeout` (optional): Timeout in seconds (default: 10)

**Example**:
```json
{
  "target": "10.0.0.1",
  "ports": "top-100",
  "rate": 1000
}
```

**Response**:
```json
{
  "success": true,
  "target": "10.0.0.1",
  "ports": [
    {"ip": "10.0.0.1", "port": 22},
    {"ip": "10.0.0.1", "port": 80}
  ],
  "open_count": 2
}
```

### 2. Curl Server (Port 8001)

**Purpose**: HTTP requests and web probing

**Tools**:
- `execute_curl`: Make HTTP requests

**Parameters**:
- `url` (required): Target URL
- `method` (optional): HTTP method (GET, POST, etc.)
- `headers` (optional): Custom headers
- `body` (optional): Request body
- `follow_redirects` (optional): Follow redirects (default: true)
- `timeout` (optional): Request timeout (default: 30)
- `verify_ssl` (optional): Verify SSL certificates (default: true)

**Example**:
```json
{
  "url": "https://example.com",
  "method": "GET",
  "headers": {"User-Agent": "AutoPenTest-AI"}
}
```

**Response**:
```json
{
  "success": true,
  "status_code": 200,
  "headers": {...},
  "body": "...",
  "body_length": 1234
}
```

### 3. Nuclei Server (Port 8002)

**Purpose**: Vulnerability scanning

**Tools**:
- `execute_nuclei`: Run vulnerability scan

**Parameters**:
- `target` (required): Target URL or IP
- `templates` (optional): Template tags (e.g., "cve", "xss")
- `severity` (optional): Minimum severity (info, low, medium, high, critical)
- `timeout` (optional): Timeout per template (default: 10)
- `rate_limit` (optional): Max requests per second (default: 150)

**Example**:
```json
{
  "target": "https://example.com",
  "templates": "cve",
  "severity": "medium"
}
```

**Response**:
```json
{
  "success": true,
  "target": "https://example.com",
  "findings": [
    {
      "template_id": "CVE-2023-1234",
      "severity": "high",
      "template_name": "Example Vulnerability"
    }
  ],
  "finding_count": 1,
  "severity_breakdown": {
    "critical": 0,
    "high": 1,
    "medium": 0
  }
}
```

### 4. Metasploit Server (Port 8003)

**Purpose**: Exploit framework integration

**Tools**:
- `search_modules`: Search for exploits/modules
- `get_module_info`: Get module details
- `check_target`: Check if target is vulnerable (safe operation)

**Example (Search)**:
```json
{
  "query": "CVE-2023-1234",
  "module_type": "exploit",
  "limit": 10
}
```

**Response**:
```json
{
  "success": true,
  "modules": [
    {
      "path": "exploit/linux/http/example_exploit",
      "description": "Example Exploit Description"
    }
  ]
}
```

## Agent Tool Integration

### Tool Registry

The tool registry manages available tools and enforces phase-based access control:

```python
from app.agent.tools.tool_registry import get_global_registry

registry = get_global_registry()

# Get tools for current phase
tools = registry.get_tools_for_phase(Phase.INFORMATIONAL)

# Check if tool is allowed
is_allowed = registry.is_tool_allowed("naabu_scan", Phase.INFORMATIONAL)
```

### Phase Restrictions

Tools are restricted to specific agent phases:

| Tool | INFORMATIONAL | EXPLOITATION | POST_EXPLOITATION |
|------|--------------|--------------|-------------------|
| echo | ✓ | ✓ | ✓ |
| calculator | ✓ | ✓ | ✓ |
| query_graph | ✓ | ✓ | ✓ |
| web_search | ✓ | ✓ | ✗ |
| naabu_scan | ✓ | ✗ | ✗ |
| http_request | ✓ | ✓ | ✗ |
| nuclei_scan | ✓ | ✓ | ✗ |
| metasploit_search | ✗ | ✓ | ✗ |

### Query Graph Tool

Queries the Neo4j attack surface graph with natural language:

```python
from app.agent.tools import QueryGraphTool

tool = QueryGraphTool(user_id="user123", project_id="proj456")
result = await tool.execute("Find all high severity vulnerabilities")
```

**Features**:
- Natural language to Cypher conversion
- Tenant filtering (user_id, project_id)
- Common query patterns (domains, vulnerabilities, ports, etc.)

### Web Search Tool

Searches the web using Tavily API:

```python
from app.agent.tools import WebSearchTool

tool = WebSearchTool()
result = await tool.execute("CVE-2023-1234 exploit details")
```

**Features**:
- CVE and vulnerability research
- Exploit information gathering
- Fallback to mock results for development

## Running MCP Servers

### Via Docker Compose

MCP servers are automatically started in the Kali tools container:

```bash
# Start all services including MCP servers
docker-compose --profile tools up -d

# Check MCP server health
curl http://localhost:8000/health  # Naabu
curl http://localhost:8001/health  # Curl
curl http://localhost:8002/health  # Nuclei
curl http://localhost:8003/health  # Metasploit
```

### Manually

To run servers manually for development:

```bash
cd backend

# Start individual servers
python -m app.mcp.servers.naabu_server
python -m app.mcp.servers.curl_server
python -m app.mcp.servers.nuclei_server
python -m app.mcp.servers.metasploit_server
```

## Testing

### Run All Tests

```bash
cd backend
pytest tests/mcp/ tests/agent/ -v
```

### Test Individual Components

```bash
# MCP base server tests
pytest tests/mcp/test_base_server.py -v

# Tool registry tests
pytest tests/agent/test_tool_registry.py -v

# Agent tools tests
pytest tests/agent/test_agent_tools.py -v
```

### Test Coverage

```bash
pytest tests/mcp/ tests/agent/ --cov=app.mcp --cov=app.agent.tools --cov-report=html
```

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Tavily API for web search
TAVILY_API_KEY=your_tavily_api_key_here

# Neo4j for graph queries
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# MCP Server URLs (if not using Docker)
NAABU_SERVER_URL=http://localhost:8000
CURL_SERVER_URL=http://localhost:8001
NUCLEI_SERVER_URL=http://localhost:8002
METASPLOIT_SERVER_URL=http://localhost:8003
```

## Security Considerations

1. **Tool Access Control**: Tools are restricted by phase to prevent unauthorized operations
2. **Input Validation**: All MCP servers validate input parameters
3. **Network Isolation**: MCP servers run in isolated Docker networks
4. **Tenant Filtering**: Graph queries include user/project filtering
5. **Safe Operations**: Metasploit server only exposes safe operations (search, check)

## API Reference

### MCPServer Base Class

```python
class MCPServer(ABC):
    def __init__(self, name: str, description: str, port: int)
    
    @abstractmethod
    def get_tools(self) -> List[MCPTool]
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]
```

### MCPClient

```python
class MCPClient:
    def __init__(self, server_url: str)
    
    async def list_tools(self) -> List[Dict[str, Any]]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]
```

### ToolRegistry

```python
class ToolRegistry:
    def register_tool(self, tool: BaseTool, allowed_phases: List[Phase] = None)
    
    def get_tools_for_phase(self, phase: Phase) -> Dict[str, BaseTool]
    
    def is_tool_allowed(self, tool_name: str, phase: Phase) -> bool
```

## Troubleshooting

### MCP Server Not Responding

1. Check if container is running:
   ```bash
   docker ps | grep kali-tools
   ```

2. Check server logs:
   ```bash
   docker logs autopentestai-kali-tools
   ```

3. Verify tools are installed in container:
   ```bash
   docker exec autopentestai-kali-tools which naabu
   docker exec autopentestai-kali-tools which nuclei
   ```

### Tool Not Available in Agent

1. Check tool registry:
   ```python
   from app.agent.tools.tool_registry import get_global_registry
   registry = get_global_registry()
   print(registry.list_all_tools())
   ```

2. Verify phase restrictions:
   ```python
   is_allowed = registry.is_tool_allowed("tool_name", current_phase)
   ```

### Connection Refused

Ensure MCP servers are in the correct Docker network and ports are exposed in docker-compose.yml.

## Future Enhancements (Month 12+)

1. **Exploit Execution**: Add controlled exploit execution with safeguards
2. **Session Management**: Metasploit session handling
3. **Payload Generation**: Dynamic payload creation
4. **Advanced RPC**: Metasploit RPC (msfrpcd) integration
5. **Tool Chaining**: Automatic tool workflow execution
6. **Result Caching**: Cache scan results to avoid redundant operations

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Naabu Documentation](https://github.com/projectdiscovery/naabu)
- [Nuclei Documentation](https://github.com/projectdiscovery/nuclei)
- [Metasploit Framework](https://www.metasploit.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

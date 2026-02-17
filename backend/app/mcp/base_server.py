"""
MCP Server Base Implementation

Provides base classes for MCP tool servers using JSON-RPC over HTTP/SSE.
"""

import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class MCPTool(BaseModel):
    """MCP Tool Definition"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for parameters")


class MCPRequest(BaseModel):
    """MCP JSON-RPC Request"""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class MCPResponse(BaseModel):
    """MCP JSON-RPC Response"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class MCPServer(ABC):
    """
    Base class for MCP tool servers.
    
    Implements JSON-RPC protocol for tool execution.
    """
    
    def __init__(self, name: str, description: str, port: int):
        """
        Initialize MCP Server.
        
        Args:
            name: Server name
            description: Server description
            port: Port to run on
        """
        self.name = name
        self.description = description
        self.port = port
        self.app = FastAPI(title=f"{name} MCP Server")
        self._setup_routes()
    
    @abstractmethod
    def get_tools(self) -> List[MCPTool]:
        """
        Get list of available tools.
        
        Returns:
            List of MCPTool definitions
        """
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of tool to execute
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        pass
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            """Health check endpoint"""
            return {
                "name": self.name,
                "description": self.description,
                "status": "healthy",
                "tools": [tool.dict() for tool in self.get_tools()]
            }
        
        @self.app.post("/rpc")
        async def rpc_handler(request: MCPRequest) -> MCPResponse:
            """
            JSON-RPC endpoint for tool execution.
            
            Handles:
            - tools/list: List available tools
            - tools/call: Execute a tool
            """
            try:
                if request.method == "tools/list":
                    tools = self.get_tools()
                    return MCPResponse(
                        result={"tools": [tool.dict() for tool in tools]},
                        id=request.id
                    )
                
                elif request.method == "tools/call":
                    if not request.params:
                        return MCPResponse(
                            error={
                                "code": -32602,
                                "message": "Invalid params: params required for tools/call"
                            },
                            id=request.id
                        )
                    
                    tool_name = request.params.get("name")
                    tool_params = request.params.get("arguments", {})
                    
                    if not tool_name:
                        return MCPResponse(
                            error={
                                "code": -32602,
                                "message": "Invalid params: 'name' is required"
                            },
                            id=request.id
                        )
                    
                    # Execute the tool
                    result = await self.execute_tool(tool_name, tool_params)
                    
                    return MCPResponse(
                        result=result,
                        id=request.id
                    )
                
                else:
                    return MCPResponse(
                        error={
                            "code": -32601,
                            "message": f"Method not found: {request.method}"
                        },
                        id=request.id
                    )
                    
            except Exception as e:
                logger.error(f"RPC handler error: {e}", exc_info=True)
                return MCPResponse(
                    error={
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    },
                    id=request.id
                )
        
        @self.app.get("/health")
        async def health():
            """Health check"""
            return {"status": "healthy", "server": self.name}
    
    def run(self):
        """Run the server"""
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


class MCPClient:
    """
    Client for communicating with MCP servers.
    """
    
    def __init__(self, server_url: str):
        """
        Initialize MCP Client.
        
        Args:
            server_url: Base URL of MCP server (e.g., http://localhost:8000)
        """
        self.server_url = server_url.rstrip("/")
        self._request_id = 0
    
    def _get_next_id(self) -> str:
        """Get next request ID"""
        self._request_id += 1
        return str(self._request_id)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from server.
        
        Returns:
            List of tool definitions
        """
        import aiohttp
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": self._get_next_id()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/rpc",
                json=request_data
            ) as response:
                result = await response.json()
                
                if "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
                
                return result.get("result", {}).get("tools", [])
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the server.
        
        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        import aiohttp
        
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": self._get_next_id()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/rpc",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 min timeout for tool execution
            ) as response:
                result = await response.json()
                
                if "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
                
                return result.get("result", {})

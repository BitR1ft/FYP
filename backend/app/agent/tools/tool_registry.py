"""
Tool Registry System

Manages dynamic tool loading and phase-based access control.
"""

from typing import Dict, List, Optional, Type
from app.agent.tools.base_tool import BaseTool
from app.agent.state.agent_state import Phase
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for managing agent tools with phase-based access control.
    """
    
    def __init__(self):
        """Initialize tool registry"""
        self._tools: Dict[str, BaseTool] = {}
        self._tool_phases: Dict[str, List[Phase]] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
    
    def register_tool(
        self, 
        tool: BaseTool, 
        allowed_phases: Optional[List[Phase]] = None
    ):
        """
        Register a tool with optional phase restrictions.
        
        Args:
            tool: Tool instance to register
            allowed_phases: List of phases where tool is available (None = all phases)
        """
        tool_name = tool.name
        self._tools[tool_name] = tool
        self._tool_phases[tool_name] = allowed_phases or list(Phase)
        self._tool_classes[tool_name] = type(tool)
        
        logger.info(f"Registered tool '{tool_name}' for phases: {[p.value for p in self._tool_phases[tool_name]]}")
    
    def unregister_tool(self, tool_name: str):
        """
        Remove a tool from registry.
        
        Args:
            tool_name: Name of tool to remove
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            del self._tool_phases[tool_name]
            del self._tool_classes[tool_name]
            logger.info(f"Unregistered tool '{tool_name}'")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Tool instance or None
        """
        return self._tools.get(tool_name)
    
    def get_tools_for_phase(self, phase: Phase) -> Dict[str, BaseTool]:
        """
        Get all tools available for a specific phase.
        
        Args:
            phase: Current agent phase
            
        Returns:
            Dictionary of tool name -> tool instance
        """
        available_tools = {}
        
        for tool_name, tool in self._tools.items():
            allowed_phases = self._tool_phases.get(tool_name, [])
            if phase in allowed_phases:
                available_tools[tool_name] = tool
        
        return available_tools
    
    def is_tool_allowed(self, tool_name: str, phase: Phase) -> bool:
        """
        Check if a tool is allowed in a specific phase.
        
        Args:
            tool_name: Name of tool
            phase: Current phase
            
        Returns:
            True if tool is allowed
        """
        if tool_name not in self._tool_phases:
            return False
        
        allowed_phases = self._tool_phases[tool_name]
        return phase in allowed_phases
    
    def list_all_tools(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def get_tool_metadata(self, tool_name: str) -> Optional[Dict]:
        """
        Get tool metadata.
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Tool metadata dictionary or None
        """
        tool = self.get_tool(tool_name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.metadata.parameters,
                "allowed_phases": [p.value for p in self._tool_phases.get(tool_name, [])]
            }
        return None
    
    def get_all_tool_metadata(self, phase: Optional[Phase] = None) -> List[Dict]:
        """
        Get metadata for all tools, optionally filtered by phase.
        
        Args:
            phase: Optional phase filter
            
        Returns:
            List of tool metadata dictionaries
        """
        if phase:
            tools = self.get_tools_for_phase(phase)
        else:
            tools = self._tools
        
        return [
            self.get_tool_metadata(tool_name)
            for tool_name in tools.keys()
        ]


def create_default_registry() -> ToolRegistry:
    """
    Create default tool registry with standard tools.
    
    Returns:
        Configured ToolRegistry instance
    """
    from app.agent.tools import (
        EchoTool, 
        CalculatorTool, 
        QueryGraphTool, 
        WebSearchTool,
        NaabuTool,
        CurlTool,
        NucleiTool,
        MetasploitTool,
        ExploitExecuteTool,
        BruteForceTool,
        SessionManagerTool,
        FileOperationsTool,
        SystemEnumerationTool,
        PrivilegeEscalationTool
    )
    
    registry = ToolRegistry()
    
    # Development/testing tools (all phases)
    registry.register_tool(
        EchoTool(),
        allowed_phases=list(Phase)
    )
    
    registry.register_tool(
        CalculatorTool(),
        allowed_phases=list(Phase)
    )
    
    # Information gathering tools (INFORMATIONAL phase)
    registry.register_tool(
        QueryGraphTool(),
        allowed_phases=[Phase.INFORMATIONAL, Phase.EXPLOITATION, Phase.POST_EXPLOITATION]
    )
    
    registry.register_tool(
        WebSearchTool(),
        allowed_phases=[Phase.INFORMATIONAL, Phase.EXPLOITATION]
    )
    
    registry.register_tool(
        NaabuTool(),
        allowed_phases=[Phase.INFORMATIONAL]
    )
    
    registry.register_tool(
        CurlTool(),
        allowed_phases=[Phase.INFORMATIONAL, Phase.EXPLOITATION]
    )
    
    registry.register_tool(
        NucleiTool(),
        allowed_phases=[Phase.INFORMATIONAL, Phase.EXPLOITATION]
    )
    
    # Exploitation tools (EXPLOITATION phase only)
    registry.register_tool(
        MetasploitTool(),
        allowed_phases=[Phase.EXPLOITATION]
    )
    
    registry.register_tool(
        ExploitExecuteTool(),
        allowed_phases=[Phase.EXPLOITATION]
    )
    
    registry.register_tool(
        BruteForceTool(),
        allowed_phases=[Phase.EXPLOITATION]
    )
    
    registry.register_tool(
        SessionManagerTool(),
        allowed_phases=[Phase.EXPLOITATION, Phase.POST_EXPLOITATION]
    )
    
    # Post-exploitation tools
    registry.register_tool(
        FileOperationsTool(),
        allowed_phases=[Phase.POST_EXPLOITATION]
    )
    
    registry.register_tool(
        SystemEnumerationTool(),
        allowed_phases=[Phase.EXPLOITATION, Phase.POST_EXPLOITATION]
    )
    
    registry.register_tool(
        PrivilegeEscalationTool(),
        allowed_phases=[Phase.POST_EXPLOITATION]
    )
    
    logger.info(f"Created default tool registry with {len(registry.list_all_tools())} tools")
    
    return registry


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_global_registry() -> ToolRegistry:
    """
    Get or create the global tool registry.
    
    Returns:
        Global ToolRegistry instance
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = create_default_registry()
    
    return _global_registry

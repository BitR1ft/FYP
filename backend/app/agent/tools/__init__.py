"""Agent tools"""

from .base_tool import BaseTool, ToolMetadata
from .error_handling import (
    ToolExecutionError,
    ToolTimeoutError,
    ToolValidationError,
    ToolRateLimitError,
    ErrorCategory,
    ToolErrorReporter,
    default_reporter,
    categorise_error,
    get_recovery_hint,
    truncate_output,
    with_timeout,
    with_error_context,
    with_retry,
)
from .echo_tool import EchoTool
from .calculator_tool import CalculatorTool
from .query_graph_tool import QueryGraphTool
from .web_search_tool import WebSearchTool
from .mcp_tools import NaabuTool, CurlTool, NucleiTool, MetasploitTool
from .exploitation_tools import ExploitExecuteTool, BruteForceTool, SessionManagerTool
from .post_exploitation_tools import FileOperationsTool, SystemEnumerationTool, PrivilegeEscalationTool

# Week 15 tool adapters (Days 93-97)
from .tool_adapters import (
    # Day 93: Recon
    DomainDiscoveryTool,
    PortScanTool,
    # Day 94: HTTP Probe
    HttpProbeTool,
    TechDetectionTool,
    EndpointEnumerationTool,
    # Day 95: Nuclei
    NucleiTemplateSelectTool,
    NucleiScanTool,
    # Day 96: Graph Query
    AttackSurfaceQueryTool,
    VulnerabilityLookupTool,
    # Day 97: Web Search
    ExploitSearchTool,
    CVELookupTool,
)

__all__ = [
    # Base
    "BaseTool",
    "ToolMetadata",
    # Error handling (Day 98)
    "ToolExecutionError",
    "ToolTimeoutError",
    "ToolValidationError",
    "ToolRateLimitError",
    "ErrorCategory",
    "ToolErrorReporter",
    "default_reporter",
    "categorise_error",
    "get_recovery_hint",
    "truncate_output",
    "with_timeout",
    "with_error_context",
    "with_retry",
    # Core tools
    "EchoTool",
    "CalculatorTool",
    "QueryGraphTool",
    "WebSearchTool",
    "NaabuTool",
    "CurlTool",
    "NucleiTool",
    "MetasploitTool",
    "ExploitExecuteTool",
    "BruteForceTool",
    "SessionManagerTool",
    "FileOperationsTool",
    "SystemEnumerationTool",
    "PrivilegeEscalationTool",
    # Week 15 adapters (Days 93-97)
    "DomainDiscoveryTool",
    "PortScanTool",
    "HttpProbeTool",
    "TechDetectionTool",
    "EndpointEnumerationTool",
    "NucleiTemplateSelectTool",
    "NucleiScanTool",
    "AttackSurfaceQueryTool",
    "VulnerabilityLookupTool",
    "ExploitSearchTool",
    "CVELookupTool",
]

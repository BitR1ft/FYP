"""
Tool Error Handling

Defines exceptions and error handling for tool execution.
Includes structured error categorization and output management.
"""

import asyncio
from functools import wraps
from typing import Callable, Any


class ToolExecutionError(Exception):
    """Raised when a tool execution fails"""
    
    def __init__(self, message: str, tool_name: str = "", recoverable: bool = True):
        self.tool_name = tool_name
        self.recoverable = recoverable
        super().__init__(message)


class ToolTimeoutError(ToolExecutionError):
    """Raised when a tool execution times out"""
    
    def __init__(self, message: str, tool_name: str = "", timeout_seconds: int = 0):
        self.timeout_seconds = timeout_seconds
        super().__init__(message, tool_name=tool_name, recoverable=True)


class ToolValidationError(ToolExecutionError):
    """Raised when tool input validation fails"""
    
    def __init__(self, message: str, tool_name: str = "", invalid_params: list = None):
        self.invalid_params = invalid_params or []
        super().__init__(message, tool_name=tool_name, recoverable=True)


def with_timeout(timeout_seconds: int = 300):
    """
    Decorator to add timeout to tool execution.
    
    Args:
        timeout_seconds: Maximum execution time in seconds (default: 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                raise ToolTimeoutError(
                    f"Tool execution timed out after {timeout_seconds} seconds",
                    timeout_seconds=timeout_seconds
                )
        return wrapper
    return decorator


def with_error_context(tool_name: str):
    """
    Decorator to add error context to tool execution.
    
    Wraps generic exceptions with ToolExecutionError including tool name.
    
    Args:
        tool_name: Name of the tool for error context
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except (ToolExecutionError, ToolTimeoutError):
                raise  # Re-raise our own exceptions
            except Exception as e:
                raise ToolExecutionError(
                    f"{tool_name} failed: {type(e).__name__}: {str(e)}",
                    tool_name=tool_name,
                    recoverable=True
                ) from e
        return wrapper
    return decorator


def truncate_output(output: str, max_chars: int = 5000) -> str:
    """
    Truncate tool output to prevent overwhelming the LLM context.
    
    Args:
        output: Tool output string
        max_chars: Maximum characters to keep
        
    Returns:
        Truncated output with indicator if truncated
    """
    if len(output) <= max_chars:
        return output
    
    # Keep first 80% and last 10% of allowed chars
    first_part_len = int(max_chars * 0.8)
    last_part_len = int(max_chars * 0.1)
    
    first_part = output[:first_part_len]
    last_part = output[-last_part_len:]
    
    truncation_msg = f"\n\n... [Output truncated: {len(output) - max_chars} chars omitted] ...\n\n"
    
    return first_part + truncation_msg + last_part

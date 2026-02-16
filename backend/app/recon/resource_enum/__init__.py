"""
Resource Enumeration Module

Comprehensive endpoint discovery using Katana, GAU, and Kiterunner.
Implements parallel execution, URL merging, deduplication, and classification.

Author: Muhammad Adeel Haider (BSCYS-F24 A)
Supervisor: Sir Galib
FYP: AutoPenTest AI - Month 6
"""

from .schemas import (
    ResourceEnumRequest,
    EndpointInfo,
    ParameterInfo,
    FormInfo,
    ResourceEnumResult,
    ResourceEnumStats,
    EnumMode,
    EndpointCategory,
    ParameterType,
)
from .katana_wrapper import KatanaWrapper
from .gau_wrapper import GAUWrapper
from .kiterunner_wrapper import KiterunnerWrapper
from .resource_orchestrator import ResourceOrchestrator

__all__ = [
    "ResourceEnumRequest",
    "EndpointInfo",
    "ParameterInfo",
    "FormInfo",
    "ResourceEnumResult",
    "ResourceEnumStats",
    "EnumMode",
    "EndpointCategory",
    "ParameterType",
    "KatanaWrapper",
    "GAUWrapper",
    "KiterunnerWrapper",
    "ResourceOrchestrator",
]

__version__ = "1.0.0"
__author__ = "Muhammad Adeel Haider"

"""
Vulnerability Scanning Module

Comprehensive vulnerability scanning with Nuclei, CVE enrichment, and MITRE mapping.

Author: Muhammad Adeel Haider (BSCYS-F24 A)
Supervisor: Sir Galib
FYP: AutoPenTest AI - Month 7
"""

from .schemas import (
    ScanMode,
    VulnSeverity,
    VulnCategory,
    VulnerabilityInfo,
    VulnScanRequest,
    VulnScanResult,
    VulnScanStats,
    CVEInfo,
    CWEInfo,
    CAPECInfo,
    MITREData,
    NucleiConfig,
    CVEEnrichmentConfig,
    MITREConfig,
)
from .nuclei_orchestrator import NucleiOrchestrator, NucleiOrchestratorConfig
from .template_updater import NucleiTemplateUpdater, TemplateVersionInfo
from .interactsh_client import InteractshClient, OOBInteraction

__all__ = [
    "ScanMode",
    "VulnSeverity",
    "VulnCategory",
    "VulnerabilityInfo",
    "VulnScanRequest",
    "VulnScanResult",
    "VulnScanStats",
    "CVEInfo",
    "CWEInfo",
    "CAPECInfo",
    "MITREData",
    "NucleiConfig",
    "CVEEnrichmentConfig",
    "MITREConfig",
    "NucleiOrchestrator",
    "NucleiOrchestratorConfig",
    "NucleiTemplateUpdater",
    "TemplateVersionInfo",
    "InteractshClient",
    "OOBInteraction",
]

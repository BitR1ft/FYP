"""
GVM/OpenVAS Scanning Schemas

Defines request/response models for GVM scanning operations.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class GvmAliveTest(str, Enum):
    """Supported alive test configurations for targets."""

    ICMP_TCP_ACK = "ICMP, TCP-ACK Service & ARP Ping"
    ICMP_ONLY = "ICMP Ping"
    TCP_ACK = "TCP-ACK Service Ping"
    CONSIDER_ALIVE = "Consider Alive"


class GvmScanProfile(str, Enum):
    """Supported scan profiles (7 default profiles)."""

    DISCOVERY = "Discovery"
    FULL_AND_FAST = "Full and fast"
    FULL_AND_VERY_DEEP = "Full and very deep"
    HOST_DISCOVERY = "Host Discovery"
    SYSTEM_DISCOVERY = "System Discovery"
    WEB_APPLICATION = "Web Application Tests"
    DATABASE = "Database Servers"


class GvmTargetConfig(BaseModel):
    """Configuration for a GVM scan target."""

    name: str = Field(..., min_length=3)
    hosts: List[str] = Field(..., min_length=1)
    port_range: str = "1-65535"
    alive_test: GvmAliveTest = GvmAliveTest.ICMP_TCP_ACK
    exclude_hosts: List[str] = Field(default_factory=list)


class GvmScanRequest(BaseModel):
    """Request model for launching a GVM scan."""

    target: GvmTargetConfig
    profile: GvmScanProfile = GvmScanProfile.FULL_AND_FAST
    scan_name: Optional[str] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    minimum_severity: Optional[str] = None
    exclude_nvt_oids: List[str] = Field(default_factory=list)
    exclude_names: List[str] = Field(default_factory=list)


class GvmScanProgress(BaseModel):
    """Progress update emitted for GVM scans."""

    task_id: str
    status: str
    progress: float
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class GvmVulnerability(BaseModel):
    """Parsed vulnerability from GVM results."""

    name: str
    severity: str
    host: str
    port: Optional[str] = None
    threat: Optional[str] = None
    cvss_score: Optional[float] = None
    cve_ids: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    nvt_oid: Optional[str] = None
    family: Optional[str] = None
    raw_severity: Optional[str] = None


class GvmScanStats(BaseModel):
    """Summary statistics for a GVM scan."""

    total_vulnerabilities: int = 0
    by_severity: Dict[str, int] = Field(default_factory=dict)
    by_threat: Dict[str, int] = Field(default_factory=dict)


class GvmScanResult(BaseModel):
    """Result payload for a GVM scan."""

    task_id: str
    report_id: Optional[str]
    vulnerabilities: List[GvmVulnerability]
    stats: GvmScanStats
    report_xml: Optional[str] = None

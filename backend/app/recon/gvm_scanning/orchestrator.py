"""GVM scan orchestration utilities."""
from __future__ import annotations

import asyncio
from typing import Optional, List

from app.api.sse import sse_manager
from app.db.neo4j_client import Neo4jClient
from app.graph.ingestion import ingest_vulnerability_scan

from .client import GvmClient
from .parser import parse_gvm_report, filter_by_severity
from .profiles import profile_display_name
from .schemas import GvmScanRequest, GvmScanResult, GvmScanStats, GvmVulnerability


class GvmScanOrchestrator:
    """Orchestrates GVM scan lifecycle."""

    def __init__(
        self,
        gvm_client: Optional[GvmClient] = None,
        poll_interval: float = 5.0,
        neo4j_client: Optional[Neo4jClient] = None,
    ):
        self.gvm_client = gvm_client or GvmClient()
        self.poll_interval = poll_interval
        self.neo4j_client = neo4j_client

    async def _emit_progress(
        self,
        project_id: Optional[str],
        task_id: str,
        status: str,
        progress: float,
        message: Optional[str] = None,
    ) -> None:
        if project_id:
            await sse_manager.send_scan_update(
                project_id,
                scan_type="gvm",
                status=status,
                data={"task_id": task_id, "progress": progress, "message": message},
            )

    async def run_scan(self, request: GvmScanRequest, report_xml_override: Optional[str] = None) -> GvmScanResult:
        target_config = request.target
        target_id = self.gvm_client.create_target(
            name=target_config.name,
            hosts=",".join(target_config.hosts),
            port_range=target_config.port_range,
            alive_test=target_config.alive_test.value,
            exclude_hosts=",".join(target_config.exclude_hosts) if target_config.exclude_hosts else None,
        )

        config_name = profile_display_name(request.profile)
        scan_configs = self.gvm_client.get_scan_configs()
        config_id = _find_config_id(scan_configs, config_name)
        if not config_id:
            raise RuntimeError(f"Scan profile '{config_name}' not found in GVM")

        scan_name = request.scan_name or f"GVM Scan - {target_config.name}"
        task_id = self.gvm_client.create_task(scan_name, target_id, config_id)
        report_id = self.gvm_client.start_task(task_id)

        await self._emit_progress(request.project_id, task_id, "started", 0.0)

        status = "Running"
        progress = 0.0
        while status not in {"Done", "Stopped", "Failed", "Interrupted"}:
            status, progress = self.gvm_client.get_task_status(task_id)
            await self._emit_progress(request.project_id, task_id, status, progress)
            if status in {"Done", "Stopped", "Failed", "Interrupted"}:
                break
            await asyncio.sleep(self.poll_interval)

        if report_xml_override is None:
            report_xml = self.gvm_client.get_report(report_id)
        else:
            report_xml = report_xml_override

        vulnerabilities = parse_gvm_report(report_xml)
        vulnerabilities = _deduplicate_vulnerabilities(vulnerabilities)
        vulnerabilities = _filter_false_positives(
            vulnerabilities,
            exclude_oids=request.exclude_nvt_oids,
            exclude_names=request.exclude_names,
        )
        if request.minimum_severity:
            vulnerabilities = filter_by_severity(vulnerabilities, request.minimum_severity.lower())
        stats = _build_stats(vulnerabilities)

        result = GvmScanResult(
            task_id=task_id,
            report_id=report_id,
            vulnerabilities=vulnerabilities,
            stats=stats,
            report_xml=report_xml,
        )

        if self.neo4j_client and vulnerabilities:
            data = {
                "vulnerabilities": [
                    {
                        "name": vuln.name,
                        "severity": vuln.severity,
                        "category": vuln.family,
                        "source": "gvm",
                        "description": vuln.description,
                        "ip": vuln.host,
                        "cve_ids": vuln.cve_ids,
                    }
                    for vuln in vulnerabilities
                ]
            }
            ingest_vulnerability_scan(self.neo4j_client, data, request.user_id, request.project_id)

        await self._emit_progress(request.project_id, task_id, "completed", 100.0)

        return result


def _find_config_id(scan_configs_xml: str, config_name: str) -> Optional[str]:
    import xml.etree.ElementTree as ET

    root = ET.fromstring(scan_configs_xml)
    for config in root.findall(".//config"):
        name = config.findtext("name")
        if name == config_name:
            return config.attrib.get("id")
    return None


def _build_stats(vulnerabilities: List[GvmVulnerability]) -> GvmScanStats:
    stats = GvmScanStats()
    for vuln in vulnerabilities:
        stats.total_vulnerabilities += 1
        stats.by_severity[vuln.severity] = stats.by_severity.get(vuln.severity, 0) + 1
        if vuln.threat:
            stats.by_threat[vuln.threat] = stats.by_threat.get(vuln.threat, 0) + 1
    return stats


def _deduplicate_vulnerabilities(
    vulnerabilities: List[GvmVulnerability],
) -> List[GvmVulnerability]:
    seen = set()
    unique = []
    for vuln in vulnerabilities:
        key = (
            vuln.host,
            vuln.port,
            vuln.nvt_oid or vuln.name,
            tuple(sorted(vuln.cve_ids)),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(vuln)
    return unique


def _filter_false_positives(
    vulnerabilities: List[GvmVulnerability],
    exclude_oids: List[str],
    exclude_names: List[str],
) -> List[GvmVulnerability]:
    exclude_oid_set = {oid.strip() for oid in exclude_oids if oid.strip()}
    exclude_name_set = {name.strip() for name in exclude_names if name.strip()}
    filtered = []
    for vuln in vulnerabilities:
        if vuln.nvt_oid and vuln.nvt_oid in exclude_oid_set:
            continue
        if vuln.name in exclude_name_set:
            continue
        filtered.append(vuln)
    return filtered

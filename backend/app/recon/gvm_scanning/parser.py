"""Parsing helpers for GVM/OpenVAS reports."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List

from .schemas import GvmVulnerability


_SEVERITY_THRESHOLDS = [
    (9.0, "critical"),
    (7.0, "high"),
    (4.0, "medium"),
    (0.1, "low"),
]


def _severity_from_score(score: float) -> str:
    for threshold, label in _SEVERITY_THRESHOLDS:
        if score >= threshold:
            return label
    return "info"


def _parse_cvss(score_text: str) -> float | None:
    try:
        return float(score_text)
    except (TypeError, ValueError):
        return None


def _extract_cve_ids(nvt_node: ET.Element) -> List[str]:
    cves: List[str] = []
    for ref in nvt_node.findall(".//ref[@type='cve']"):
        ref_id = ref.attrib.get("id", "")
        if ref_id:
            for cve in ref_id.split(","):
                cve = cve.strip()
                if cve:
                    cves.append(cve.upper())
    return list(dict.fromkeys(cves))


def parse_gvm_report(report_xml: str) -> List[GvmVulnerability]:
    """Parse GVM XML report into structured vulnerabilities."""
    root = ET.fromstring(report_xml)
    vulnerabilities: List[GvmVulnerability] = []

    for result in root.findall(".//result"):
        host = result.findtext("host", default="")
        port = result.findtext("port")
        threat = result.findtext("threat")
        raw_severity = result.findtext("severity")

        nvt_node = result.find("nvt")
        if nvt_node is None:
            continue

        name = nvt_node.findtext("name", default="Unknown vulnerability")
        cvss_text = nvt_node.findtext("cvss_base") or raw_severity
        cvss_score = _parse_cvss(cvss_text)
        severity_label = _severity_from_score(cvss_score or 0.0)
        description = nvt_node.findtext("description") or result.findtext("description")
        family = nvt_node.findtext("family")
        nvt_oid = nvt_node.attrib.get("oid")
        cve_ids = _extract_cve_ids(nvt_node)

        vulnerabilities.append(
            GvmVulnerability(
                name=name,
                severity=severity_label,
                host=host,
                port=port,
                threat=threat,
                cvss_score=cvss_score,
                cve_ids=cve_ids,
                description=description,
                nvt_oid=nvt_oid,
                family=family,
                raw_severity=raw_severity,
            )
        )

    return vulnerabilities


def filter_by_severity(vulnerabilities: List[GvmVulnerability], minimum: str) -> List[GvmVulnerability]:
    """Filter vulnerabilities by minimum severity label."""
    order = ["info", "low", "medium", "high", "critical"]
    if minimum not in order:
        return vulnerabilities
    min_index = order.index(minimum)
    return [v for v in vulnerabilities if order.index(v.severity) >= min_index]

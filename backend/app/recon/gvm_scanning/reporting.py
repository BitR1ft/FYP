"""Report generation helpers for GVM scan results."""
from __future__ import annotations

from typing import Iterable
import xml.etree.ElementTree as ET

from .schemas import GvmScanResult


def generate_xml_report(result: GvmScanResult) -> str:
    """Generate an XML report from scan results."""
    root = ET.Element("gvm_report", attrib={"task_id": result.task_id})
    stats = ET.SubElement(root, "stats")
    ET.SubElement(stats, "total").text = str(result.stats.total_vulnerabilities)

    for severity, count in result.stats.by_severity.items():
        ET.SubElement(stats, "severity", attrib={"level": severity}).text = str(count)

    vulns_node = ET.SubElement(root, "vulnerabilities")
    for vuln in result.vulnerabilities:
        vuln_node = ET.SubElement(vulns_node, "vulnerability")
        ET.SubElement(vuln_node, "name").text = vuln.name
        ET.SubElement(vuln_node, "severity").text = vuln.severity
        ET.SubElement(vuln_node, "host").text = vuln.host
        if vuln.port:
            ET.SubElement(vuln_node, "port").text = vuln.port
        if vuln.cvss_score is not None:
            ET.SubElement(vuln_node, "cvss_score").text = str(vuln.cvss_score)
        if vuln.threat:
            ET.SubElement(vuln_node, "threat").text = vuln.threat
        if vuln.description:
            ET.SubElement(vuln_node, "description").text = vuln.description
        for cve_id in vuln.cve_ids:
            ET.SubElement(vuln_node, "cve").text = cve_id

    return ET.tostring(root, encoding="unicode")


def generate_html_report(result: GvmScanResult) -> str:
    """Generate a simple HTML report from scan results."""
    rows = []
    for vuln in result.vulnerabilities:
        rows.append(
            "<tr>"
            f"<td>{vuln.name}</td>"
            f"<td>{vuln.severity}</td>"
            f"<td>{vuln.host}</td>"
            f"<td>{vuln.port or '-'}</td>"
            f"<td>{vuln.cvss_score or '-'}</td>"
            f"<td>{', '.join(vuln.cve_ids) or '-'}</td>"
            "</tr>"
        )

    return (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'><title>GVM Scan Report</title>"
        "<style>table{border-collapse:collapse;width:100%;}"
        "th,td{border:1px solid #ddd;padding:8px;}"
        "th{background:#f4f4f4;text-align:left;}</style>"
        "</head><body>"
        f"<h1>GVM Scan Report</h1><p>Task ID: {result.task_id}</p>"
        f"<p>Total vulnerabilities: {result.stats.total_vulnerabilities}</p>"
        "<table><thead><tr>"
        "<th>Name</th><th>Severity</th><th>Host</th><th>Port</th><th>CVSS</th><th>CVEs</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></body></html>"
    )


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(lines: Iterable[str]) -> bytes:
    """Build a minimal PDF with the supplied lines."""
    y_offset = 720
    content_lines = ["BT", "/F1 11 Tf", f"72 {y_offset} Td"]
    for line in lines:
        content_lines.append(f"({_escape_pdf_text(line)}) Tj")
        content_lines.append("0 -14 Td")
    content_lines.append("ET")
    stream = "\n".join(content_lines)
    stream_bytes = stream.encode("latin-1")

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream_bytes)} >>\nstream\n{stream}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    xref_positions = [0]
    body = []
    current_pos = len("%PDF-1.4\n")
    for index, obj in enumerate(objects, start=1):
        obj_text = f"{index} 0 obj\n{obj}\nendobj\n"
        body.append(obj_text)
        xref_positions.append(current_pos)
        current_pos += len(obj_text.encode("latin-1"))

    xref_lines = ["xref", f"0 {len(objects) + 1}", "0000000000 65535 f "]
    for pos in xref_positions[1:]:
        xref_lines.append(f"{pos:010d} 00000 n ")

    trailer = (
        "trailer\n"
        f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        "startxref\n"
        f"{current_pos}\n%%EOF\n"
    )

    pdf_bytes = "%PDF-1.4\n".encode("latin-1")
    pdf_bytes += "".join(body).encode("latin-1")
    pdf_bytes += "\n".join(xref_lines).encode("latin-1")
    pdf_bytes += "\n".encode("latin-1")
    pdf_bytes += trailer.encode("latin-1")
    return pdf_bytes


def generate_pdf_report(result: GvmScanResult) -> bytes:
    """Generate a minimal PDF report from scan results."""
    max_entries = 50
    lines = [
        "GVM Scan Report",
        f"Task ID: {result.task_id}",
        f"Total vulnerabilities: {result.stats.total_vulnerabilities}",
        "",
    ]
    for vuln in result.vulnerabilities[:max_entries]:
        lines.append(f"{vuln.severity.upper()}: {vuln.name} ({vuln.host})")
    if len(result.vulnerabilities) > max_entries:
        lines.append("")
        lines.append(f"Note: Report truncated to {max_entries} findings.")
    return _build_pdf(lines)

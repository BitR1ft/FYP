from app.recon.gvm_scanning.reporting import (
    generate_html_report,
    generate_pdf_report,
    generate_xml_report,
)
from app.recon.gvm_scanning.schemas import GvmScanResult, GvmScanStats, GvmVulnerability


def _sample_result() -> GvmScanResult:
    vuln = GvmVulnerability(
        name="Sample Vuln",
        severity="high",
        host="10.0.0.1",
        port="443/tcp",
        cvss_score=8.1,
        cve_ids=["CVE-2024-0002"],
    )
    stats = GvmScanStats(total_vulnerabilities=1, by_severity={"high": 1}, by_threat={})
    return GvmScanResult(task_id="task-123", report_id="report-1", vulnerabilities=[vuln], stats=stats)


def test_generate_xml_report_contains_vulnerability():
    result = _sample_result()
    xml_report = generate_xml_report(result)
    assert "Sample Vuln" in xml_report
    assert "CVE-2024-0002" in xml_report


def test_generate_html_report_contains_table():
    result = _sample_result()
    html_report = generate_html_report(result)
    assert "<table>" in html_report
    assert "Sample Vuln" in html_report


def test_generate_pdf_report_starts_with_pdf_header():
    result = _sample_result()
    pdf_bytes = generate_pdf_report(result)
    assert pdf_bytes.startswith(b"%PDF")

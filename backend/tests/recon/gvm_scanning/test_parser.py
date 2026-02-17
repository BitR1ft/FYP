from app.recon.gvm_scanning.parser import parse_gvm_report


REPORT_XML = """
<report>
  <results>
    <result>
      <host>192.168.1.10</host>
      <port>80/tcp</port>
      <severity>9.8</severity>
      <threat>High</threat>
      <nvt oid="1.3.6.1.4.1.25623.1.0.100000">
        <name>Test Vulnerability</name>
        <family>General</family>
        <description>Test description</description>
        <refs>
          <ref type="cve" id="CVE-2023-0001" />
        </refs>
      </nvt>
    </result>
    <result>
      <host>192.168.1.20</host>
      <port>22/tcp</port>
      <severity>5.4</severity>
      <threat>Medium</threat>
      <nvt oid="1.3.6.1.4.1.25623.1.0.100001">
        <name>Second Vulnerability</name>
        <family>SSH</family>
        <description>Another description</description>
      </nvt>
    </result>
  </results>
</report>
"""


def test_parse_gvm_report_extracts_vulnerabilities():
    results = parse_gvm_report(REPORT_XML)

    assert len(results) == 2
    first = results[0]
    assert first.name == "Test Vulnerability"
    assert first.severity == "critical"
    assert first.host == "192.168.1.10"
    assert first.port == "80/tcp"
    assert first.cve_ids == ["CVE-2023-0001"]

    second = results[1]
    assert second.severity == "medium"
    assert second.family == "SSH"

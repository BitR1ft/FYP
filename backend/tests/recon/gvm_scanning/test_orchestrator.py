import pytest

from app.recon.gvm_scanning.orchestrator import GvmScanOrchestrator
from app.recon.gvm_scanning.schemas import GvmScanRequest, GvmTargetConfig, GvmScanProfile

REPORT_XML = """
<report>
  <results>
    <result>
      <host>10.0.0.5</host>
      <port>443/tcp</port>
      <severity>7.5</severity>
      <threat>High</threat>
      <nvt oid="1.3.6.1.4.1.25623.1.0.100002">
        <name>TLS Weak Cipher</name>
        <family>SSL</family>
        <description>Weak cipher suite detected</description>
        <refs>
          <ref type="cve" id="CVE-2024-1111" />
        </refs>
      </nvt>
    </result>
  </results>
</report>
"""


class FakeGvmClient:
    def create_target(self, **kwargs):
        return "target-1"

    def get_scan_configs(self):
        return """
        <scan_configs>
          <config id='config-1'>
            <name>Full and fast</name>
          </config>
        </scan_configs>
        """

    def create_task(self, name, target_id, config_id):
        return "task-1"

    def start_task(self, task_id):
        return "report-1"

    def get_task_status(self, task_id):
        return "Done", 100.0

    def get_report(self, report_id):
        return REPORT_XML


@pytest.mark.asyncio
async def test_orchestrator_runs_with_fake_client():
    request = GvmScanRequest(
        target=GvmTargetConfig(name="Lab", hosts=["10.0.0.5"]),
        profile=GvmScanProfile.FULL_AND_FAST,
    )
    orchestrator = GvmScanOrchestrator(gvm_client=FakeGvmClient(), poll_interval=0)
    result = await orchestrator.run_scan(request)

    assert result.task_id == "task-1"
    assert result.report_id == "report-1"
    assert result.stats.total_vulnerabilities == 1
    assert result.vulnerabilities[0].name == "TLS Weak Cipher"

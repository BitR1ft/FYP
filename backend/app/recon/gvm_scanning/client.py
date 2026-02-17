"""
GVM/OpenVAS client wrapper using python-gvm.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import xml.etree.ElementTree as ET

from app.core.config import settings

try:
    from gvm.connections import TLSConnection, UnixSocketConnection
    from gvm.protocols.gmp import Gmp
except ImportError as exc:  # pragma: no cover - handled in runtime
    TLSConnection = None
    UnixSocketConnection = None
    Gmp = None
    _gvm_import_error = exc
else:
    _gvm_import_error = None


@dataclass
class GvmConnectionConfig:
    """Configuration for connecting to GVM manager."""

    host: str
    port: int
    username: str
    password: str
    socket_path: Optional[str] = None


class GvmClientError(RuntimeError):
    """Raised when a GVM operation fails."""


class GvmClient:
    """Thin wrapper around python-gvm GMP client."""

    def __init__(self, config: Optional[GvmConnectionConfig] = None):
        if _gvm_import_error:
            raise GvmClientError(
                "python-gvm is required for GVM integration. "
                "Install it from requirements.txt."
            ) from _gvm_import_error

        if config is None:
            config = GvmConnectionConfig(
                host=settings.GVM_HOST,
                port=settings.GVM_PORT,
                username=settings.GVM_USERNAME,
                password=settings.GVM_PASSWORD,
                socket_path=settings.GVM_SOCKET_PATH or None,
            )
        self.config = config

    def _connection(self):
        if self.config.socket_path:
            return UnixSocketConnection(path=self.config.socket_path)
        return TLSConnection(hostname=self.config.host, port=self.config.port)

    def _connect(self) -> Gmp:
        if Gmp is None:
            raise GvmClientError("python-gvm is not available")
        connection = self._connection()
        gmp = Gmp(connection=connection)
        gmp.authenticate(self.config.username, self.config.password)
        return gmp

    @staticmethod
    def _extract_id(xml_payload: str) -> str:
        root = ET.fromstring(xml_payload)
        node_id = root.attrib.get("id")
        if node_id:
            return node_id
        id_node = root.find(".//*[@id]")
        if id_node is not None:
            return id_node.attrib.get("id", "")
        raise GvmClientError("Unable to extract ID from GVM response")

    def get_version(self) -> str:
        with self._connect() as gmp:
            response = gmp.get_version()
        root = ET.fromstring(response)
        return root.findtext("version", default="unknown")

    def create_target(
        self,
        name: str,
        hosts: str,
        port_range: str,
        alive_test: str,
        exclude_hosts: Optional[str] = None,
    ) -> str:
        with self._connect() as gmp:
            response = gmp.create_target(
                name=name,
                hosts=hosts,
                port_range=port_range,
                alive_test=alive_test,
                exclude_hosts=exclude_hosts,
            )
        return self._extract_id(response)

    def create_task(self, name: str, target_id: str, config_id: str) -> str:
        with self._connect() as gmp:
            response = gmp.create_task(name=name, target_id=target_id, config_id=config_id)
        return self._extract_id(response)

    def start_task(self, task_id: str) -> str:
        with self._connect() as gmp:
            response = gmp.start_task(task_id)
        root = ET.fromstring(response)
        report_id = root.attrib.get("report_id") or root.attrib.get("id")
        if report_id:
            return report_id
        return self._extract_id(response)

    def get_task_status(self, task_id: str) -> Tuple[str, float]:
        with self._connect() as gmp:
            response = gmp.get_task(task_id)
        root = ET.fromstring(response)
        status = root.findtext(".//status", default="Unknown")
        progress_text = root.findtext(".//progress", default="0")
        try:
            progress = float(progress_text)
        except ValueError:
            progress = 0.0
        return status, progress

    def get_report(self, report_id: str, report_format_id: Optional[str] = None) -> str:
        with self._connect() as gmp:
            response = gmp.get_report(report_id=report_id, report_format_id=report_format_id)
        return response

    def get_report_formats(self) -> str:
        with self._connect() as gmp:
            return gmp.get_report_formats()

    def get_scan_configs(self) -> str:
        with self._connect() as gmp:
            return gmp.get_scan_configs()

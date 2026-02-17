"""API endpoints for GVM/OpenVAS scanning."""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import logging

from app.db.neo4j_client import Neo4jClient
from app.recon.gvm_scanning import (
    GvmScanOrchestrator,
    GvmScanRequest,
    generate_html_report,
    generate_pdf_report,
    generate_xml_report,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gvm", tags=["gvm"])


class GvmScanStatusResponse(BaseModel):
    scan_id: str
    status: str
    task_id: Optional[str] = None
    report_id: Optional[str] = None
    error: Optional[str] = None
    updated_at: str


class GvmScanStartResponse(BaseModel):
    scan_id: str
    status: str
    created_at: str


_scan_status: Dict[str, GvmScanStatusResponse] = {}
_scan_results: Dict[str, object] = {}
# In-memory scan state; replace with persistent storage in production deployments.
_scan_lock = asyncio.Lock()


async def _run_scan(scan_id: str, request: GvmScanRequest) -> None:
    async with _scan_lock:
        status = _scan_status[scan_id]
        status.status = "running"
        status.updated_at = datetime.utcnow().isoformat()

    neo4j_client: Optional[Neo4jClient] = None
    try:
        neo4j_client = Neo4jClient()
        neo4j_client.connect()
    except Exception as exc:
        logger.warning("Neo4j connection unavailable for GVM ingestion: %s", exc)
        neo4j_client = None

    try:
        orchestrator = GvmScanOrchestrator(neo4j_client=neo4j_client)
        result = await orchestrator.run_scan(request)
        async with _scan_lock:
            _scan_results[scan_id] = result
            status.task_id = result.task_id
            status.report_id = result.report_id
            status.status = "completed"
    except Exception as exc:
        logger.error("GVM scan failed: %s", exc)
        async with _scan_lock:
            status.status = "failed"
            status.error = str(exc)
    finally:
        async with _scan_lock:
            status.updated_at = datetime.utcnow().isoformat()
        if neo4j_client:
            neo4j_client.close()


@router.post("/scans", response_model=GvmScanStartResponse)
async def start_gvm_scan(request: GvmScanRequest):
    scan_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()
    async with _scan_lock:
        _scan_status[scan_id] = GvmScanStatusResponse(
            scan_id=scan_id,
            status="queued",
            updated_at=created_at,
        )

    asyncio.create_task(_run_scan(scan_id, request))

    return GvmScanStartResponse(scan_id=scan_id, status="queued", created_at=created_at)


@router.get("/scans/{scan_id}", response_model=GvmScanStatusResponse)
async def get_gvm_scan_status(scan_id: str):
    async with _scan_lock:
        status = _scan_status.get(scan_id)
    if not status:
        raise HTTPException(status_code=404, detail="Scan not found")
    return status


@router.get("/scans/{scan_id}/report")
async def get_gvm_scan_report(scan_id: str, format: str = "html"):
    async with _scan_lock:
        result = _scan_results.get(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Report not available")

    format = format.lower()
    if format == "raw":
        return Response(content=result.report_xml or "", media_type="application/xml")
    if format == "xml":
        return Response(content=generate_xml_report(result), media_type="application/xml")
    if format == "pdf":
        pdf_bytes = generate_pdf_report(result)
        return Response(content=pdf_bytes, media_type="application/pdf")

    html_report = generate_html_report(result)
    return HTMLResponse(content=html_report)

# GVM/OpenVAS Scanning Module (Month 13)

This module integrates **GVM/OpenVAS** into AutoPenTest-AI to provide enterprise-grade network vulnerability scanning.

## Features

- GMP client wrapper (python-gvm)
- Target + task orchestration
- Scan profile mapping (7 profiles)
- XML result parsing and filtering
- Report generation (XML/HTML/PDF)
- Optional Neo4j ingestion
- SSE progress updates

## Usage

```python
from app.recon.gvm_scanning import GvmScanOrchestrator, GvmScanRequest

orchestrator = GvmScanOrchestrator()
result = await orchestrator.run_scan(GvmScanRequest(...))
```

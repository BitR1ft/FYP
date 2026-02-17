# GVM/OpenVAS User Guide (Month 13)

## 🎯 Purpose

This guide explains how to run **GVM/OpenVAS** network vulnerability scans inside AutoPenTest-AI, including container setup, scan profiles, report formats, and troubleshooting tips.

---

## ✅ Prerequisites

- Docker + Docker Compose
- GVM service enabled in `docker-compose.yml`
- `.env` configured with GVM credentials

---

## 🚀 Quick Start

```bash
# Start the GVM container
docker compose up -d gvm

# Verify ports
# GMP: 9390
# Web UI: http://localhost:9392
```

**Default credentials:**
- Username: `admin`
- Password: value of `GVM_PASSWORD` in `.env`

**Environment variables:**
- `GVM_HOST` (default: `gvm`)
- `GVM_PORT` (default: `9390`)
- `GVM_USERNAME`
- `GVM_PASSWORD`
- `GVM_SOCKET_PATH` (optional for UNIX socket)

---

## 🧭 Scan Profiles (7 Default Profiles)

| Profile | Purpose |
| --- | --- |
| Discovery | Lightweight asset discovery |
| Full and fast | Default balanced scan |
| Full and very deep | Deep scan for exhaustive testing |
| Host Discovery | Only host discovery probes |
| System Discovery | OS and service fingerprinting |
| Web Application Tests | Web-focused checks |
| Database Servers | Database-specific checks |

---

## 🧪 Running Scans via API

```http
POST /api/gvm/scans
```

Example payload:
```json
{
  "target": {
    "name": "Internal Lab",
    "hosts": ["192.168.1.10"],
    "port_range": "1-65535",
    "alive_test": "ICMP, TCP-ACK Service & ARP Ping"
  },
  "profile": "Full and fast",
  "minimum_severity": "medium",
  "exclude_nvt_oids": ["1.3.6.1.4.1.25623.1.0.100000"],
  "exclude_names": ["False Positive Example"],
  "project_id": "<project-id>",
  "user_id": "<user-id>"
}
```

Check status:
```http
GET /api/gvm/scans/{scan_id}
```

Fetch report formats:
```http
GET /api/gvm/scans/{scan_id}/report?format=html
GET /api/gvm/scans/{scan_id}/report?format=xml
GET /api/gvm/scans/{scan_id}/report?format=pdf
```

---

## 📡 Real-Time Progress Streaming

Connect to SSE for scan updates:

```
GET /api/sse/stream/scans/{project_id}
```

Events include:
- `scan_type`: `gvm`
- `status`: `running`, `completed`, `failed`
- `progress`: percentage (0-100)

---

## ✅ False Positive Management

Use the request filters to suppress known false positives:

- `exclude_nvt_oids`: ignore specific NVT identifiers
- `exclude_names`: ignore vulnerabilities by name
- `minimum_severity`: drop informational/low findings

---

## 📁 Report Outputs

- **XML:** structured vulnerability details
- **HTML:** human-readable table output
- **PDF:** lightweight summary export

Reports are stored in the `gvm-reports` Docker volume for archival.

---

## 🔄 NVT Feed Synchronization

The first feed sync can take several hours. Monitor the container logs to verify
that NVTs are downloading and updating:

```bash
docker compose logs -f gvm
```

---

## 🛠️ Troubleshooting

| Issue | Resolution |
| --- | --- |
| GVM not starting | Ensure Docker has ≥4GB RAM allocated |
| GMP connection refused | Confirm port 9390 is open and credentials are valid |
| No results returned | Confirm targets are reachable and alive test is correct |
| Slow feed sync | Allow first sync to run for several hours; use nightly updates |

---

## ✅ Best Practices

- Use **Discovery** for quick host validation
- Run **Full and fast** as the baseline scan
- Schedule **Full and very deep** overnight
- Archive reports after ingestion into Neo4j

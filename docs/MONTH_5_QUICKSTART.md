# Month 5 Quick Start Guide

## HTTP Probing Module

### Installation Verification

```bash
# Verify httpx is installed
httpx -version

# Verify Wappalyzer is installed
wappalyzer --version

# Verify Python dependencies
pip list | grep -E "(pydantic|httpx|mmh3|cryptography)"
```

### Quick Usage Examples

#### 1. Python API

```python
import asyncio
from app.recon.http_probing import HttpProbeOrchestrator, HttpProbeRequest, ProbeMode

async def main():
    # Create probe request
    request = HttpProbeRequest(
        targets=["https://example.com", "https://google.com"],
        mode=ProbeMode.FULL,
        tech_detection=True,
        wappalyzer=True,
        tls_inspection=True,
        favicon_hash=True
    )
    
    # Execute probe
    orchestrator = HttpProbeOrchestrator(request)
    result = await orchestrator.run()
    
    # Access results
    for target in result.results:
        print(f"\n{'='*60}")
        print(f"URL: {target.url}")
        print(f"Status: {target.status_code}")
        print(f"Server: {target.server_header}")
        print(f"Title: {target.content.title if target.content else 'N/A'}")
        
        if target.technologies:
            print(f"\nTechnologies ({len(target.technologies)}):")
            for tech in target.technologies:
                print(f"  - {tech.name} {tech.version or ''} [{tech.category}]")
        
        if target.tls and target.tls.certificate:
            cert = target.tls.certificate
            print(f"\nTLS Certificate:")
            print(f"  Issuer: {cert.issuer}")
            print(f"  Expires in: {cert.days_until_expiry} days")
        
        if target.security_headers:
            print(f"\nSecurity Score: {target.security_headers.security_score}/100")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 2. CLI Usage

```bash
# Basic probe
python -m app.recon.http_probing.cli probe https://example.com

# Probe multiple targets
python -m app.recon.http_probing.cli probe https://example.com https://google.com

# Probe from file
echo "https://example.com" > targets.txt
echo "https://google.com" >> targets.txt
python -m app.recon.http_probing.cli probe -f targets.txt

# Full probe with verbose output and JSON export
python -m app.recon.http_probing.cli probe https://example.com \
  --mode full \
  --verbose \
  -o results.json

# Disable specific features
python -m app.recon.http_probing.cli probe https://example.com \
  --no-wappalyzer \
  --no-favicon \
  --timeout 5

# Custom threading
python -m app.recon.http_probing.cli probe -f targets.txt \
  --threads 100 \
  --timeout 15
```

#### 3. REST API Usage

```bash
# Start async probe
curl -X POST http://localhost:8000/api/http-probe/probe \
  -H "Content-Type: application/json" \
  -d '{
    "targets": ["https://example.com"],
    "mode": "full",
    "tech_detection": true,
    "wappalyzer": true,
    "tls_inspection": true,
    "favicon_hash": true
  }'

# Response:
# {
#   "task_id": "http_probe_1234567890",
#   "status": "started",
#   "message": "HTTP probe started for 1 target(s)"
# }

# Check progress
curl http://localhost:8000/api/http-probe/results/http_probe_1234567890

# Quick synchronous probe (max 10 targets)
curl -X POST http://localhost:8000/api/http-probe/quick-probe \
  -H "Content-Type: application/json" \
  -d '{
    "targets": ["https://example.com"],
    "mode": "full"
  }'

# List all tasks
curl http://localhost:8000/api/http-probe/tasks

# Delete results
curl -X DELETE http://localhost:8000/api/http-probe/results/http_probe_1234567890
```

### Integration with Other Modules

#### With Port Scanning

```python
from app.recon.port_scanning import PortScanOrchestrator, PortScanRequest
from app.recon.http_probing import HttpProbeOrchestrator, HttpProbeRequest

# Step 1: Port scan
port_request = PortScanRequest(targets=["192.168.1.1"])
port_results = await PortScanOrchestrator(port_request).run()

# Step 2: Extract HTTP/HTTPS services
urls = []
for ip_result in port_results.results:
    for port in ip_result.ports:
        if port.port in [80, 443, 8080, 8443]:
            scheme = "https" if port.port in [443, 8443] else "http"
            urls.append(f"{scheme}://{ip_result.ip}:{port.port}")

# Step 3: HTTP probe
http_request = HttpProbeRequest(targets=urls)
http_results = await HttpProbeOrchestrator(http_request).run()
```

#### With Domain Discovery

```python
from app.recon.domain_discovery import DomainDiscovery
from app.recon.http_probing import HttpProbeOrchestrator, HttpProbeRequest

# Step 1: Domain discovery
discovery = DomainDiscovery(domain="example.com")
discovery_results = await discovery.run()

# Step 2: Extract subdomains
targets = list(discovery_results['subdomains'].keys())

# Step 3: HTTP probe
http_request = HttpProbeRequest(targets=targets)
http_results = await HttpProbeOrchestrator(http_request).run()
```

### Common Use Cases

#### 1. Security Assessment

```python
# Focus on security headers and TLS
request = HttpProbeRequest(
    targets=["https://mysite.com"],
    mode=ProbeMode.FULL,
    tls_inspection=True,
    security_headers=True,
    jarm_fingerprint=True
)

result = await HttpProbeOrchestrator(request).run()

# Check security score
for target in result.results:
    if target.security_headers:
        score = target.security_headers.security_score
        if score < 50:
            print(f"WARNING: Low security score ({score}/100)")
            print(f"Missing: {target.security_headers.missing_headers}")
```

#### 2. Technology Profiling

```python
# Focus on technology detection
request = HttpProbeRequest(
    targets=["https://target.com"],
    mode=ProbeMode.FULL,
    tech_detection=True,
    wappalyzer=True
)

result = await HttpProbeOrchestrator(request).run()

# Analyze technologies
for target in result.results:
    print(f"Technologies for {target.url}:")
    for tech in target.technologies:
        print(f"  {tech.name} {tech.version or ''} - {tech.category}")
```

#### 3. Favicon-Based Reconnaissance

```python
# Focus on favicon hashing
request = HttpProbeRequest(
    targets=["https://target.com"],
    mode=ProbeMode.BASIC,
    favicon_hash=True
)

result = await HttpProbeOrchestrator(request).run()

# Get Shodan query
for target in result.results:
    if target.favicon and target.favicon.mmh3:
        print(f"Shodan query: http.favicon.hash:{target.favicon.mmh3}")
```

### Troubleshooting

#### httpx not found
```bash
# Install Go
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Install httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
export PATH=$PATH:~/go/bin
```

#### Wappalyzer not found
```bash
# Install Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Wappalyzer
npm install -g wappalyzer
```

#### Python dependencies
```bash
pip install pydantic httpx cryptography mmh3
```

### Performance Tips

1. **Parallel Execution**: Use higher thread count for faster probing
   ```bash
   python -m app.recon.http_probing.cli probe -f targets.txt --threads 200
   ```

2. **Mode Selection**: Use appropriate mode for your use case
   - `basic`: Fast, minimal data
   - `full`: Comprehensive, slower
   - `stealth`: Minimal footprint

3. **Selective Features**: Disable unnecessary features
   ```python
   request = HttpProbeRequest(
       targets=targets,
       mode=ProbeMode.BASIC,
       wappalyzer=False,  # Skip if not needed
       screenshot=False,   # Always skip unless required
       favicon_hash=False  # Skip if not needed
   )
   ```

### Output Format

The probe returns a `HttpProbeResult` object with:

```python
{
    "request": HttpProbeRequest,
    "results": [BaseURLInfo],  # List of probe results
    "stats": HttpProbeStats,    # Statistics
    "started_at": datetime,
    "completed_at": datetime
}
```

Each `BaseURLInfo` contains:
- URL information (scheme, host, port)
- HTTP response metadata
- Content information
- TLS certificate details
- Detected technologies
- Security headers
- Favicon hashes
- Redirect chains

### Documentation

- **Module README**: `backend/app/recon/http_probing/README.md`
- **Complete Report**: `docs/MONTH_5_COMPLETE.md`
- **Summary**: `docs/MONTH_5_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs (when running)

---

**Quick Reference Card**

| Task | Command |
|------|---------|
| Basic probe | `python -m app.recon.http_probing.cli probe URL` |
| File input | `python -m app.recon.http_probing.cli probe -f file.txt` |
| JSON output | `python -m app.recon.http_probing.cli probe URL -o out.json` |
| Verbose | `python -m app.recon.http_probing.cli probe URL -v` |
| API probe | `POST /api/http-probe/probe` |
| Get results | `GET /api/http-probe/results/{task_id}` |

---

For more information, see the comprehensive documentation in the `docs/` directory.

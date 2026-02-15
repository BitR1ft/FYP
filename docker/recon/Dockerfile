# ==============================================================================
# Reconnaissance Container
# Purpose: Dedicated container for reconnaissance tools and scripts
# ==============================================================================

FROM python:3.11-slim-bookworm

LABEL maintainer="Muhammad Adeel Haider"
LABEL description="AutoPenTest AI - Reconnaissance Container"
LABEL version="1.0.0"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ==============================================================================
# SYSTEM DEPENDENCIES
# ==============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential tools
    ca-certificates \
    curl \
    wget \
    git \
    # Build tools
    build-essential \
    gcc \
    g++ \
    # Network tools
    nmap \
    dnsutils \
    iputils-ping \
    netcat-traditional \
    whois \
    # Other utilities
    jq \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# PYTHON ENVIRONMENT
# ==============================================================================
# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies for reconnaissance
RUN pip install --no-cache-dir \
    # HTTP libraries
    requests \
    httpx \
    aiohttp \
    # HTML parsing
    beautifulsoup4 \
    lxml \
    # DNS tools
    dnspython \
    # Async libraries
    asyncio \
    aiofiles \
    # Network libraries
    python-nmap \
    python-whois \
    # Data handling
    pydantic \
    # Utilities
    colorama \
    termcolor \
    rich \
    tqdm \
    # Subdomain enumeration libraries
    sublist3r

# ==============================================================================
# GO TOOLS INSTALLATION
# ==============================================================================
# Install Go for modern recon tools
RUN wget -q https://go.dev/dl/go1.21.6.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz && \
    rm go1.21.6.linux-amd64.tar.gz

# Set up Go environment
ENV GOPATH=/root/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Install modern reconnaissance tools
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/tomnomnom/assetfinder@latest && \
    go install -v github.com/tomnomnom/waybackurls@latest && \
    go install -v github.com/tomnomnom/httprobe@latest && \
    go install -v github.com/ffuf/ffuf/v2@latest

# Update nuclei templates
RUN nuclei -update-templates || true

# ==============================================================================
# WORKSPACE SETUP
# ==============================================================================
# Create working directories
RUN mkdir -p /app /results/recon /configs

# Set working directory
WORKDIR /app

# ==============================================================================
# ENTRYPOINT SCRIPT
# ==============================================================================
# Create entrypoint script for recon container
RUN echo '#!/bin/bash\n\
set -e\n\
echo "=== AutoPenTest AI - Reconnaissance Container ==="\n\
echo "Container started at: $(date)"\n\
echo "Tools available:"\n\
echo "  - Subfinder: $(subfinder -version 2>&1 | head -1)"\n\
echo "  - Nuclei: $(nuclei -version 2>&1 | head -1)"\n\
echo "  - Naabu: $(naabu -version 2>&1 | head -1)"\n\
echo "  - Httpx: $(httpx -version 2>&1 | head -1)"\n\
echo "  - Nmap: $(nmap --version | head -1)"\n\
echo "  - Python: $(python --version)"\n\
echo ""\n\
echo "Ready to receive reconnaissance tasks..."\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# ==============================================================================
# HEALTH CHECK
# ==============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD subfinder -version || exit 1

# ==============================================================================
# RUNTIME CONFIGURATION
# ==============================================================================
ENTRYPOINT ["/entrypoint.sh"]
CMD ["tail", "-f", "/dev/null"]

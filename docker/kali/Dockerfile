# ==============================================================================
# Kali Linux Security Tools Container
# Purpose: Base container with essential penetration testing tools
# ==============================================================================

FROM kalilinux/kali-rolling:latest

LABEL maintainer="Muhammad Adeel Haider"
LABEL description="AutoPenTest AI - Kali Linux Tools Container"
LABEL version="1.0.0"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm-256color

# Update and upgrade system
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get dist-upgrade -y

# ==============================================================================
# ESSENTIAL SYSTEM TOOLS
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Core utilities
    ca-certificates \
    curl \
    wget \
    git \
    vim \
    nano \
    tmux \
    screen \
    net-tools \
    iputils-ping \
    dnsutils \
    traceroute \
    netcat-traditional \
    socat \
    telnet \
    ftp \
    # Build tools
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    # Python ecosystem
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    # Other essentials
    jq \
    unzip \
    zip \
    p7zip-full \
    tar \
    gzip

# ==============================================================================
# NETWORK RECONNAISSANCE TOOLS
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Port scanning
    nmap \
    masscan \
    # Network discovery
    netdiscover \
    arp-scan \
    # DNS enumeration
    dnsrecon \
    dnsenum \
    fierce \
    # SSL/TLS testing
    sslscan \
    sslyze \
    testssl.sh \
    # Service enumeration
    enum4linux \
    nbtscan \
    onesixtyone \
    snmp

# ==============================================================================
# WEB APPLICATION TESTING TOOLS
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Web scanners
    nikto \
    dirb \
    dirbuster \
    gobuster \
    wfuzz \
    # Web proxies
    burpsuite \
    zaproxy \
    # Web crawlers
    whatweb \
    wafw00f \
    # Subdomain enumeration
    sublist3r \
    # HTTP clients
    httpie

# ==============================================================================
# EXPLOITATION FRAMEWORKS
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Metasploit Framework
    metasploit-framework \
    # Exploit databases
    exploitdb \
    # Social engineering
    set

# ==============================================================================
# PASSWORD CRACKING & BRUTE FORCING
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Password crackers
    john \
    hashcat \
    hydra \
    medusa \
    # Hash identification
    hashid \
    hash-identifier \
    # Wordlists
    wordlists \
    # Credential tools
    crunch

# ==============================================================================
# WIRELESS SECURITY TOOLS
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Wireless tools
    aircrack-ng \
    reaver \
    pixiewps \
    # Bluetooth tools
    bluez \
    bluez-tools

# ==============================================================================
# FORENSICS & ANALYSIS TOOLS
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Forensics
    autopsy \
    sleuthkit \
    # Binary analysis
    binwalk \
    foremost \
    # Network analysis
    wireshark \
    tshark \
    tcpdump \
    # Steganography
    steghide \
    stegosuite

# ==============================================================================
# POST-EXPLOITATION TOOLS
# ==============================================================================
RUN apt-get install -y --no-install-recommends \
    # Privilege escalation
    unix-privesc-check \
    # Persistence
    weevely \
    # Data exfiltration
    dnschef

# ==============================================================================
# PYTHON SECURITY LIBRARIES
# ==============================================================================
RUN pip3 install --no-cache-dir --break-system-packages \
    # Core libraries
    requests \
    beautifulsoup4 \
    lxml \
    # Network libraries
    scapy \
    impacket \
    # Web libraries
    selenium \
    mechanize \
    # Exploitation libraries
    pwntools \
    # Cryptography
    pycryptodome \
    # Other utilities
    colorama \
    termcolor \
    python-nmap \
    python-whois

# ==============================================================================
# ADDITIONAL MODERN TOOLS
# ==============================================================================
# Install Go (for modern tools like nuclei, subfinder, etc.)
RUN apt-get install -y --no-install-recommends golang-go

# Set up Go environment
ENV GOPATH=/root/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Install modern reconnaissance tools
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install -v github.com/tomnomnom/waybackurls@latest && \
    go install -v github.com/tomnomnom/httprobe@latest && \
    go install -v github.com/ffuf/ffuf/v2@latest

# Update nuclei templates
RUN nuclei -update-templates

# ==============================================================================
# WORDLISTS SETUP
# ==============================================================================
# Extract SecLists (common wordlists for security testing)
RUN mkdir -p /usr/share/wordlists && \
    cd /usr/share/wordlists && \
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git

# Uncompress rockyou wordlist if compressed
RUN if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then \
        gunzip /usr/share/wordlists/rockyou.txt.gz; \
    fi

# ==============================================================================
# CLEANUP
# ==============================================================================
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# ==============================================================================
# WORKSPACE SETUP
# ==============================================================================
# Create working directories
RUN mkdir -p /results /configs /root/tools

# Set working directory
WORKDIR /root

# ==============================================================================
# HEALTH CHECK
# ==============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD nmap --version || exit 1

# ==============================================================================
# METADATA
# ==============================================================================
# Document installed tool versions
RUN echo "=== Kali Tools Container - Installed Versions ===" > /root/tool-versions.txt && \
    echo "Nmap: $(nmap --version | head -1)" >> /root/tool-versions.txt && \
    echo "Metasploit: $(msfconsole --version)" >> /root/tool-versions.txt && \
    echo "Nuclei: $(nuclei --version)" >> /root/tool-versions.txt && \
    echo "Python: $(python3 --version)" >> /root/tool-versions.txt && \
    echo "Go: $(go version)" >> /root/tool-versions.txt

# Default command (keep container running)
CMD ["tail", "-f", "/dev/null"]

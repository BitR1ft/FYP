# ==============================================================================
# AutoPenTest AI Backend - FastAPI Application
# Purpose: Main API server with WebSocket, SSE, and Docker SDK support
# ==============================================================================

FROM python:3.11-slim-bookworm

LABEL maintainer="Muhammad Adeel Haider"
LABEL description="AutoPenTest AI - FastAPI Backend"
LABEL version="1.0.0"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ==============================================================================
# SYSTEM DEPENDENCIES
# ==============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    gcc \
    g++ \
    make \
    # PostgreSQL client
    postgresql-client \
    libpq-dev \
    # Network tools
    curl \
    wget \
    # Other utilities
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# PYTHON ENVIRONMENT
# ==============================================================================
# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Docker SDK for Python (for container orchestration)
RUN pip install --no-cache-dir docker

# ==============================================================================
# APPLICATION CODE
# ==============================================================================
# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/autopentestai /app/.cache

# ==============================================================================
# RUNTIME USER (Security)
# ==============================================================================
# Create non-root user for running the application
RUN useradd -m -u 1000 autopentestai && \
    chown -R autopentestai:autopentestai /app /var/log/autopentestai

# ==============================================================================
# EXPOSE PORTS
# ==============================================================================
EXPOSE 8000

# ==============================================================================
# HEALTH CHECK
# ==============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ==============================================================================
# RUNTIME CONFIGURATION
# ==============================================================================
# Switch to non-root user
USER autopentestai

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

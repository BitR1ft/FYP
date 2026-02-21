"""
AutoPenTest AI - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
from datetime import datetime

from app.core.config import settings
from app.api import auth, projects, graph, agent
from app.api import recon as recon_api
from app.api import port_scan as port_scan_api
from app.api import http_probe as http_probe_api
from app.api import scans_ports as scans_ports_api
from app.api import scans_nuclei as scans_nuclei_api
from app.api import discovery_urls as discovery_urls_api
from app.api import cve_enrichment as cve_enrichment_api
from app.api import enrichment_api as enrichment_cwe_api
from app.api.sse import router as sse_router
from app.websocket import router as ws_router
from app.db import neo4j_client
from app.db.prisma_client import get_prisma, disconnect_prisma
from app.middleware import setup_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
setup_middleware(app)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "AutoPenTest AI API",
        "status": "operational",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    # Check Neo4j health
    neo4j_health = neo4j_client.health_check()

    # Check Prisma / PostgreSQL connectivity
    db_status = "not_configured"
    try:
        db = await get_prisma()
        await db.execute_raw("SELECT 1")
        db_status = "healthy"
    except Exception as exc:
        logger.warning("PostgreSQL health check failed: %s", exc)
        db_status = "unavailable"

    overall = (
        "healthy"
        if neo4j_health.get("healthy", False) and db_status == "healthy"
        else "degraded"
    )

    return {
        "status": overall,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "services": {
            "api": "operational",
            "database": db_status,
            "neo4j": neo4j_health.get("status", "unknown"),
        },
        "details": {
            "neo4j": neo4j_health,
        },
    }


@app.get("/readiness", tags=["Health"])
async def readiness_check():
    """
    Kubernetes-style readiness probe.

    Returns 200 only when **all** required services (PostgreSQL and Neo4j) are
    reachable.  Returns 503 otherwise so that load balancers / orchestrators can
    route traffic away from an unready pod.
    """
    checks: dict = {}
    ready = True

    # PostgreSQL via Prisma
    try:
        db = await get_prisma()
        await db.execute_raw("SELECT 1")
        checks["postgresql"] = "ready"
    except Exception as exc:
        logger.warning("Readiness: PostgreSQL not ready – %s", exc)
        checks["postgresql"] = "not_ready"
        ready = False

    # Neo4j
    neo4j_health = neo4j_client.health_check()
    if neo4j_health.get("healthy"):
        checks["neo4j"] = "ready"
    else:
        checks["neo4j"] = "not_ready"
        ready = False

    if not ready:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": checks,
            },
        )

    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# Internal helper: connect Prisma with exponential-backoff retries
# ---------------------------------------------------------------------------

async def _connect_prisma_with_retry(max_attempts: int = 5, base_delay: float = 2.0) -> None:
    """
    Attempt to establish the Prisma / PostgreSQL connection, retrying with
    exponential back-off if the database is not yet available (e.g. during
    Docker Compose start-up).
    """
    for attempt in range(1, max_attempts + 1):
        try:
            await get_prisma()
            logger.info("Prisma client connected to PostgreSQL (attempt %d)", attempt)
            return
        except Exception as exc:
            if attempt == max_attempts:
                logger.error(
                    "Prisma connection failed after %d attempts: %s", max_attempts, exc
                )
                logger.warning("Application starting without PostgreSQL connectivity")
                return
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                "PostgreSQL not ready (attempt %d/%d), retrying in %.1fs – %s",
                attempt, max_attempts, delay, exc,
            )
            await asyncio.sleep(delay)


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(graph.router, prefix="/api", tags=["Graph Database"])
app.include_router(recon_api.router, tags=["Reconnaissance"])
app.include_router(port_scan_api.router, tags=["Port Scanning"])
app.include_router(http_probe_api.router, tags=["HTTP Probing"])
app.include_router(scans_ports_api.router, tags=["Port Scans"])
app.include_router(scans_nuclei_api.router, tags=["Nuclei Scans"])
app.include_router(discovery_urls_api.router, tags=["URL Discovery"])
app.include_router(cve_enrichment_api.router, tags=["CVE Enrichment"])
app.include_router(enrichment_cwe_api.router, tags=["CWE/CAPEC Enrichment"])
app.include_router(agent.router, prefix="/api", tags=["AI Agent"])
app.include_router(sse_router, prefix="/api/sse", tags=["Server-Sent Events"])
app.include_router(ws_router, tags=["WebSocket"])


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize Neo4j connection
    try:
        neo4j_client.connect()
        logger.info("Neo4j connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j: {e}")
        logger.warning("Application starting without Neo4j connectivity")

    # Initialize Prisma / PostgreSQL connection (with retry)
    await _connect_prisma_with_retry()
    
    logger.info("Application startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down application")
    
    # Close Neo4j connection
    try:
        neo4j_client.close()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Error closing Neo4j connection: {e}")

    # Disconnect Prisma client
    try:
        await disconnect_prisma()
    except Exception as e:
        logger.error(f"Error disconnecting Prisma: {e}")
    
    logger.info("Shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

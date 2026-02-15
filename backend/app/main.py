"""
AutoPenTest AI - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from app.core.config import settings
from app.api import auth, projects
from app.api import recon as recon_api
from app.api import port_scan as port_scan_api
from app.api.sse import router as sse_router
from app.websocket import router as ws_router
from app.db import neo4j_client
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
    
    return {
        "status": "healthy" if neo4j_health.get('healthy', False) else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "services": {
            "api": "operational",
            "database": "not_configured",  # Will update when Prisma is connected
            "neo4j": neo4j_health.get('status', 'unknown')
        },
        "details": {
            "neo4j": neo4j_health
        }
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(recon_api.router, tags=["Reconnaissance"])
app.include_router(port_scan_api.router, tags=["Port Scanning"])
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
    
    logger.info("Shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

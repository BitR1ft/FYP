"""
Reconnaissance API Endpoints

Provides REST API endpoints for domain discovery and reconnaissance operations.
Integrates with WebSocket for real-time progress updates.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.recon.domain_discovery import DomainDiscovery
from app.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recon", tags=["reconnaissance"])


class ReconRequest(BaseModel):
    """Request model for reconnaissance operations."""
    domain: str = Field(..., description="Target domain for reconnaissance")
    hackertarget_api_key: Optional[str] = Field(None, description="HackerTarget API key")
    dns_nameservers: Optional[list[str]] = Field(None, description="Custom DNS nameservers")


class ReconResponse(BaseModel):
    """Response model for reconnaissance operations."""
    status: str
    message: str
    task_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# In-memory task storage (will be replaced with database in production)
recon_tasks = {}


@router.post("/discover", response_model=ReconResponse)
async def start_domain_discovery(
    request: ReconRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Start domain discovery for a target domain.
    
    This endpoint initiates a background task for comprehensive domain discovery
    including WHOIS lookup, subdomain enumeration, and DNS resolution.
    """
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        logger.info(f"Starting domain discovery for {request.domain} (task: {task_id})")
        
        # Store task status
        recon_tasks[task_id] = {
            "status": "pending",
            "domain": request.domain,
            "user_id": current_user.get("user_id"),
            "progress": 0,
            "results": None
        }
        
        # Start background task
        background_tasks.add_task(
            run_domain_discovery,
            task_id,
            request.domain,
            request.hackertarget_api_key,
            request.dns_nameservers
        )
        
        return ReconResponse(
            status="success",
            message=f"Domain discovery started for {request.domain}",
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"Error starting domain discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=ReconResponse)
async def get_recon_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the status of a reconnaissance task.
    
    Returns the current status, progress, and results (if completed).
    """
    if task_id not in recon_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = recon_tasks[task_id]
    
    # Check if user owns this task
    if task["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    return ReconResponse(
        status=task["status"],
        message=f"Task progress: {task['progress']}%",
        task_id=task_id,
        data=task.get("results")
    )


@router.get("/results/{task_id}")
async def get_recon_results(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the full results of a completed reconnaissance task.
    """
    if task_id not in recon_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = recon_tasks[task_id]
    
    # Check if user owns this task
    if task["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    return task.get("results", {})


async def run_domain_discovery(
    task_id: str,
    domain: str,
    hackertarget_api_key: Optional[str] = None,
    dns_nameservers: Optional[list] = None
):
    """
    Background task to run domain discovery.
    
    Updates task status and stores results upon completion.
    """
    try:
        logger.info(f"Running domain discovery for {domain} (task: {task_id})")
        
        # Update status
        recon_tasks[task_id]["status"] = "running"
        recon_tasks[task_id]["progress"] = 10
        
        # Initialize discovery
        discovery = DomainDiscovery(
            domain=domain,
            hackertarget_api_key=hackertarget_api_key,
            dns_nameservers=dns_nameservers
        )
        
        # Run discovery
        recon_tasks[task_id]["progress"] = 25
        results = await discovery.run()
        
        # Store results
        recon_tasks[task_id]["status"] = "completed"
        recon_tasks[task_id]["progress"] = 100
        recon_tasks[task_id]["results"] = results
        
        logger.info(f"Domain discovery completed for {domain} (task: {task_id})")
        
    except Exception as e:
        logger.error(f"Error in domain discovery task {task_id}: {str(e)}")
        recon_tasks[task_id]["status"] = "failed"
        recon_tasks[task_id]["error"] = str(e)


@router.delete("/tasks/{task_id}")
async def delete_recon_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a reconnaissance task and its results.
    """
    if task_id not in recon_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = recon_tasks[task_id]
    
    # Check if user owns this task
    if task["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    del recon_tasks[task_id]
    
    return {"status": "success", "message": "Task deleted"}


@router.get("/tasks")
async def list_recon_tasks(current_user: dict = Depends(get_current_user)):
    """
    List all reconnaissance tasks for the current user.
    """
    user_id = current_user.get("user_id")
    user_tasks = {
        task_id: {
            "task_id": task_id,
            "domain": task["domain"],
            "status": task["status"],
            "progress": task["progress"]
        }
        for task_id, task in recon_tasks.items()
        if task["user_id"] == user_id
    }
    
    return {"tasks": list(user_tasks.values())}

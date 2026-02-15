"""
Projects API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import List, Optional
import uuid

from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    Message,
    ProjectStatus
)
from app.core.security import decode_token

router = APIRouter()
security = HTTPBearer()

# In-memory project storage (will be replaced with database)
projects_db: dict = {}


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency to get current user ID from token"""
    token_data = decode_token(credentials.credentials)
    user_id = token_data.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return user_id


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new penetration testing project
    
    - **name**: Project name
    - **description**: Optional project description
    - **target**: Target domain, IP, or URL
    - **project_type**: Type of assessment (default: full_assessment)
    """
    project_id = str(uuid.uuid4())
    
    project = {
        "id": project_id,
        "user_id": user_id,
        "name": project_data.name,
        "description": project_data.description,
        "target": project_data.target,
        "project_type": project_data.project_type,
        "status": ProjectStatus.DRAFT.value,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        
        # Reconnaissance settings
        "enable_subdomain_enum": project_data.enable_subdomain_enum,
        "enable_port_scan": project_data.enable_port_scan,
        "enable_web_crawl": project_data.enable_web_crawl,
        "enable_tech_detection": project_data.enable_tech_detection,
        
        # Scanning settings
        "enable_vuln_scan": project_data.enable_vuln_scan,
        "enable_nuclei": project_data.enable_nuclei,
        
        # Exploitation settings
        "enable_auto_exploit": project_data.enable_auto_exploit,
    }
    
    projects_db[project_id] = project
    
    return ProjectResponse(**project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ProjectStatus] = None
):
    """
    List all projects for the current user
    
    Supports pagination and filtering by status
    """
    # Filter projects by user
    user_projects = [
        p for p in projects_db.values()
        if p['user_id'] == user_id
    ]
    
    # Filter by status if provided
    if status:
        user_projects = [p for p in user_projects if p['status'] == status.value]
    
    # Sort by updated_at descending
    user_projects.sort(key=lambda x: x['updated_at'], reverse=True)
    
    # Pagination
    total = len(user_projects)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_projects = user_projects[start:end]
    
    return ProjectListResponse(
        projects=[ProjectResponse(**p) for p in paginated_projects],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific project by ID
    """
    project = projects_db.get(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return ProjectResponse(**project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a project
    
    Only name, description, and status can be updated
    """
    project = projects_db.get(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project"
        )
    
    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and isinstance(value, ProjectStatus):
            project[field] = value.value
        else:
            project[field] = value
    
    project['updated_at'] = datetime.utcnow()
    
    return ProjectResponse(**project)


@router.delete("/{project_id}", response_model=Message)
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a project
    """
    project = projects_db.get(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    # Delete project
    del projects_db[project_id]
    
    return Message(message="Project deleted successfully")

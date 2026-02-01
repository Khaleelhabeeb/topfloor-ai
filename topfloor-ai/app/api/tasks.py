from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DBSession
from typing import Optional

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatus
)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task.
    
    Tasks represent work to be done by agents. Creating a task:
    1. Validates the agent type
    2. Creates a task record
    3. Optionally starts agent execution (if auto_start is enabled)
    
    Returns the created task with its ID and initial status.
    """
    from app.agents import AgentRegistry
    from datetime import datetime, timezone
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(task_data.agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {task_data.agent_type}"
        )
    
    # TODO: Implement actual task creation in database
    # For now, return a placeholder response
    
    return TaskResponse(
        id=1,  # Placeholder
        title=task_data.title,
        description=task_data.description,
        agent_type=task_data.agent_type,
        status=TaskStatus.PENDING,
        priority=task_data.priority,
        session_id=None,
        result=None,
        error=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        completed_at=None
    )


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List tasks for the current user.
    
    Supports filtering by:
    - Status (pending, in_progress, completed, failed, cancelled)
    - Agent type
    
    Results are paginated.
    """
    # TODO: Implement actual task listing from database
    # For now, return empty list
    
    return TaskListResponse(
        tasks=[],
        total=0,
        page=page,
        page_size=page_size
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by ID.
    
    Returns detailed information about the task including:
    - Current status
    - Associated session
    - Results (if completed)
    - Error information (if failed)
    """
    # TODO: Implement actual task retrieval
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task.
    
    Allows updating:
    - Title and description
    - Status (e.g., to cancel a task)
    - Priority
    - Result data
    """
    # TODO: Implement actual task update
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.
    
    This is a hard delete. For soft delete, use PATCH to set status to cancelled.
    """
    # TODO: Implement actual task deletion
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DBSession
from typing import Optional

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.task import TaskStatus as TaskStatusEnum, TaskPriority, TaskType
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatus
)
from app.services.task_service import TaskService
from app.workers.background_worker import enqueue_task, get_queue_status, cancel_task


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task and enqueue it for processing.
    
    Tasks represent work to be done by agents. Creating a task:
    1. Validates the agent type
    2. Creates a task record
    3. Enqueues the task for background processing
    
    Returns the created task with its ID and initial status.
    """
    from app.agents import AgentRegistry
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(task_data.agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {task_data.agent_type}"
        )
    
    # Create task service
    task_service = TaskService(db)
    
    # Create task in database
    task = task_service.create_task(
        user_id=current_user.id,
        task_data=task_data
    )
    
    # Enqueue task for background processing if it's a background task
    if task.task_type == TaskType.BACKGROUND:
        try:
            queue_result = enqueue_task(task.id)
            if not queue_result.get("queued", True):
                task.status = TaskStatusEnum.PENDING
                db.commit()
        except Exception:
            task.status = TaskStatusEnum.PENDING
            db.commit()
    
    # Convert to response schema
    return TaskResponse(
        id=task.id,
        task_id=task.task_id,
        title=task.title,
        description=task.description,
        agent_type=task.agent_type,
        task_type=task.task_type.value,
        status=TaskStatus(task.status.value),
        priority=task.priority.value,
        progress=task.progress,
        due_date=task.due_date,
        input_data=task.input_data,
        result_data=task.result_data,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at
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
    # Create task service
    task_service = TaskService(db)
    
    # Convert status to enum if provided
    status_enum = None
    if status:
        status_enum = TaskStatusEnum(status.value)
    
    # Get tasks with pagination
    skip = (page - 1) * page_size
    tasks, total = task_service.get_tasks(
        user_id=current_user.id,
        agent_type=agent_type,
        status=status_enum,
        skip=skip,
        limit=page_size
    )
    
    # Convert to response schema
    task_responses = [
        TaskResponse(
            id=task.id,
            task_id=task.task_id,
            title=task.title,
            description=task.description,
            agent_type=task.agent_type,
            task_type=task.task_type.value,
            status=TaskStatus(task.status.value),
            priority=task.priority.value,
            progress=task.progress,
            due_date=task.due_date,
            input_data=task.input_data,
            result_data=task.result_data,
            error_message=task.error_message,
            created_at=task.created_at,
            updated_at=task.updated_at,
            started_at=task.started_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/agents/{agent_type}", response_model=TaskListResponse)
async def get_agent_tasks(
    agent_type: str,
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all tasks for a specific agent type.
    
    This endpoint allows filtering tasks by agent type and optionally by status.
    Useful for viewing all tasks assigned to a particular agent.
    """
    from app.agents import AgentRegistry
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    # Create task service
    task_service = TaskService(db)
    
    # Convert status to enum if provided
    status_enum = None
    if status:
        status_enum = TaskStatusEnum(status.value)
    
    # Get tasks with pagination
    skip = (page - 1) * page_size
    tasks, total = task_service.get_tasks(
        user_id=current_user.id,
        agent_type=agent_type,
        status=status_enum,
        skip=skip,
        limit=page_size
    )
    
    # Convert to response schema
    task_responses = [
        TaskResponse(
            id=task.id,
            task_id=task.task_id,
            title=task.title,
            description=task.description,
            agent_type=task.agent_type,
            task_type=task.task_type.value,
            status=TaskStatus(task.status.value),
            priority=task.priority.value,
            progress=task.progress,
            due_date=task.due_date,
            input_data=task.input_data,
            result_data=task.result_data,
            error_message=task.error_message,
            created_at=task.created_at,
            updated_at=task.updated_at,
            started_at=task.started_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/agents/{agent_type}/queue", response_model=dict)
async def get_agent_queue_status(
    agent_type: str,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the queue status for a specific agent.
    
    Returns:
    - Agent status (available, busy, idle)
    - Current task being processed
    - Number of tasks in queue
    - List of queued tasks
    """
    from app.agents import AgentRegistry
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    try:
        queue_status = get_queue_status(current_user.id, agent_type)
        return queue_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get queue status: {str(e)}"
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
    # Create task service
    task_service = TaskService(db)
    
    # Get task
    task = task_service.get_task_by_id(task_id, user_id=current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Convert to response schema
    return TaskResponse(
        id=task.id,
        task_id=task.task_id,
        title=task.title,
        description=task.description,
        agent_type=task.agent_type,
        task_type=task.task_type.value,
        status=TaskStatus(task.status.value),
        priority=task.priority.value,
        progress=task.progress,
        due_date=task.due_date,
        input_data=task.input_data,
        result_data=task.result_data,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at
    )


@router.get("/{task_id}/status", response_model=dict)
async def get_task_status(
    task_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a specific task.
    
    Returns a lightweight response with just the status information,
    useful for polling task progress without fetching the full task object.
    """
    # Create task service
    task_service = TaskService(db)
    
    # Get task
    task = task_service.get_task_by_id(task_id, user_id=current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Calculate progress percentage based on status
    progress_map = {
        TaskStatusEnum.PENDING: 0,
        TaskStatusEnum.QUEUED: 10,
        TaskStatusEnum.IN_PROGRESS: 50,
        TaskStatusEnum.COMPLETED: 100,
        TaskStatusEnum.FAILED: 100,
        TaskStatusEnum.CANCELLED: 100
    }
    
    status_progress = progress_map.get(task.status, 0)
    stored_progress = task.progress if task.progress is not None else 0

    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "progress": max(status_progress, stored_progress),
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "error_message": task.error_message if task.status == TaskStatusEnum.FAILED else None
    }


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
    # Create task service
    task_service = TaskService(db)
    
    # Update task
    task = task_service.update_task(
        task_id=task_id,
        user_id=current_user.id,
        task_update=task_update
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Convert to response schema
    return TaskResponse(
        id=task.id,
        task_id=task.task_id,
        title=task.title,
        description=task.description,
        agent_type=task.agent_type,
        task_type=task.task_type.value,
        status=TaskStatus(task.status.value),
        priority=task.priority.value,
        progress=task.progress,
        due_date=task.due_date,
        input_data=task.input_data,
        result_data=task.result_data,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at
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
    # Create task service
    task_service = TaskService(db)
    
    # Delete task
    deleted = task_service.delete_task(task_id, user_id=current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return None


@router.post("/{task_id}/cancel", response_model=dict)
async def cancel_task_endpoint(
    task_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a pending or queued task.
    
    Returns cancellation status.
    """
    try:
        result = cancel_task(task_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )

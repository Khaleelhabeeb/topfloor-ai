"""
CEO API - Endpoints for CEO dashboard data
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import time
import uuid

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.task_history import TaskHistory
from app.services.task_service import TaskService
from app.agents import AgentRegistry
from app.agents.factory import AgentFactory
from app.agents.registry import AgentType
from app.adk.runner import AgentRunner


router = APIRouter(prefix="/ceo", tags=["CEO"])


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {value}"
        ) from exc


def _status_progress(status: TaskStatus) -> int:
    progress_map = {
        TaskStatus.PENDING: 0,
        TaskStatus.QUEUED: 10,
        TaskStatus.IN_PROGRESS: 50,
        TaskStatus.COMPLETED: 100,
        TaskStatus.FAILED: 100,
        TaskStatus.CANCELLED: 100
    }
    return progress_map.get(status, 0)


def _activity_from_history(
    history: TaskHistory,
    task: Task,
    actor: str
) -> Dict[str, Any]:
    metadata = history.event_metadata or {}
    action_type = metadata.get("action_type")

    if not action_type:
        if history.status == TaskStatus.COMPLETED.value:
            action_type = "task_completed"
        elif history.status == TaskStatus.CANCELLED.value:
            action_type = "task_cancelled"
        else:
            action_type = "task_updated"

    if action_type == "task_assigned":
        action = f"Assigned new task to {task.agent_type}"
    elif action_type == "task_completed":
        action = f"Task completed by {task.agent_type}"
    elif action_type == "task_cancelled":
        action = f"Task cancelled for {task.agent_type}"
    else:
        action = f"Task updated for {task.agent_type}"

    details = history.message or task.title

    merged_metadata = {
        "task_id": task.task_id,
        "status": task.status.value,
        "priority": task.priority.value,
    }
    merged_metadata.update(metadata)

    return {
        "id": f"activity_{history.id}",
        "timestamp": history.created_at.isoformat(),
        "action_type": action_type,
        "action": action,
        "details": details,
        "actor": actor,
        "target_agent": task.agent_type,
        "metadata": merged_metadata,
    }


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_ceo_dashboard(
    include_tasks: bool = Query(True, description="Include detailed task list"),
    include_activity: bool = Query(True, description="Include recent activity"),
    activity_limit: int = Query(10, ge=1, le=100, description="Number of activity entries"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get CEO dashboard overview data.
    """
    task_service = TaskService(db)
    tasks, total = task_service.get_tasks(
        user_id=current_user.id,
        sort_by="created_at",
        sort_order="desc",
        limit=1000
    )

    completed = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
    in_progress = sum(1 for task in tasks if task.status == TaskStatus.IN_PROGRESS)
    pending = sum(1 for task in tasks if task.status == TaskStatus.PENDING)

    progress_values = [max(task.progress or 0, _status_progress(task.status)) for task in tasks]
    average_progress = int(round(sum(progress_values) / len(progress_values))) if progress_values else 0

    last_updated = max((task.updated_at for task in tasks if task.updated_at), default=None)
    last_updated_iso = last_updated.isoformat() if last_updated else datetime.now(timezone.utc).isoformat()

    agent_definitions = {agent.agent_type.value: agent for agent in AgentRegistry.get_all_agents()}
    tasks_by_agent: List[Dict[str, Any]] = []
    grouped: Dict[str, List[Task]] = {}
    for task in tasks:
        grouped.setdefault(task.agent_type, []).append(task)

    for agent_type, agent_tasks in grouped.items():
        agent_def = agent_definitions.get(agent_type)
        agent_name = agent_type.replace("_", " ").title()
        agent_role = agent_name
        if agent_def:
            agent_name = agent_def.name.replace("_", " ").title()
            agent_role = agent_def.agent_type.value.replace("_", " ").title()

        task_items = []
        if include_tasks:
            for task in agent_tasks:
                task_items.append({
                    "id": task.task_id,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "progress": max(task.progress or 0, _status_progress(task.status)),
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                })

        tasks_by_agent.append({
            "agent_id": agent_type,
            "agent_type": agent_type,
            "agent_name": agent_name,
            "agent_role": agent_role,
            "task_count": len(agent_tasks),
            "tasks": task_items
        })

    recent_activity: List[Dict[str, Any]] = []
    if include_activity:
        recent_activity = _get_activity_feed(
            db=db,
            current_user=current_user,
            limit=activity_limit
        )

    return {
        "overview": {
            "total_tasks": total,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "pending_tasks": pending,
            "average_progress": average_progress,
            "last_updated": last_updated_iso
        },
        "tasks_by_agent": tasks_by_agent,
        "recent_activity": recent_activity
    }


def _get_activity_feed(
    db: DBSession,
    current_user: User,
    limit: int
) -> List[Dict[str, Any]]:
    rows = (
        db.query(TaskHistory, Task)
        .join(Task, TaskHistory.task_id == Task.id)
        .filter(Task.user_id == current_user.id)
        .order_by(TaskHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    actor = current_user.email
    return [_activity_from_history(history, task, actor) for history, task in rows]


@router.get("/activity", response_model=Dict[str, Any])
async def get_ceo_activity(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    date_from: Optional[str] = Query(None, description="Start date (ISO 8601)"),
    date_to: Optional[str] = Query(None, description="End date (ISO 8601)"),
    agent_id: Optional[str] = Query(None, description="Filter by agent type"),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated CEO activity history.
    """
    start_date = _parse_iso_datetime(date_from)
    end_date = _parse_iso_datetime(date_to)

    query = (
        db.query(TaskHistory, Task)
        .join(Task, TaskHistory.task_id == Task.id)
        .filter(Task.user_id == current_user.id)
    )

    if start_date:
        query = query.filter(TaskHistory.created_at >= start_date)
    if end_date:
        query = query.filter(TaskHistory.created_at <= end_date)
    if agent_id:
        query = query.filter(Task.agent_type == agent_id)

    rows = query.order_by(TaskHistory.created_at.desc()).all()

    actor = current_user.email
    activities = []
    for history, task in rows:
        activity = _activity_from_history(history, task, actor)
        if action_type and activity["action_type"] != action_type:
            continue
        activities.append(activity)

    total = len(activities)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = activities[start:end]
    total_pages = (total + page_size - 1) // page_size

    return {
        "activities": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.post("/chat", response_model=Dict[str, Any])
async def ceo_chat(
    payload: Dict[str, Any],
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a CEO message to one or more agents.
    """
    message = payload.get("message")
    if not message or not isinstance(message, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="message is required"
        )

    mentioned_agents = payload.get("mentioned_agents") or []
    if not isinstance(mentioned_agents, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="mentioned_agents must be a list"
        )

    context = payload.get("context") if isinstance(payload.get("context"), dict) else None

    if not mentioned_agents:
        mentioned_agents = ["orchestrator"]

    for agent_type in mentioned_agents:
        if not AgentRegistry.validate_agent_type(agent_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid agent type: {agent_type}"
            )

    agent_factory = AgentFactory()
    responses = []
    for agent_type in mentioned_agents:
        session_id = f"ceo_chat_{uuid.uuid4().hex[:12]}"
        agent_type_enum = AgentType(agent_type)

        if agent_type_enum == AgentType.ORCHESTRATOR:
            from app.services.task_service import TaskService
            from app.services.agent_status_service import AgentStatusService

            task_service = TaskService(db)
            agent_status_service = AgentStatusService(db)
            agent = agent_factory.create_agent_team(
                user_context={"user_id": current_user.id},
                task_service=task_service,
                agent_status_service=agent_status_service
            )
        elif agent_type_enum == AgentType.TEAM_LEAD:
            from app.services.task_service import TaskService
            from app.services.agent_status_service import AgentStatusService

            task_service = TaskService(db)
            agent_status_service = AgentStatusService(db)
            agent = agent_factory.create_agent(
                agent_type_enum,
                user_context={"user_id": current_user.id},
                task_service=task_service,
                agent_status_service=agent_status_service
            )
        else:
            agent = agent_factory.create_agent(
                agent_type_enum,
                user_context={"user_id": current_user.id}
            )
        runner = AgentRunner(
            agent=agent,
            session_id=session_id,
            user_id=current_user.id,
            agent_type=agent_type,
            enable_memory=False
        )
        start_time = time.monotonic()
        result = runner.run(message=message, context=context)
        elapsed = time.monotonic() - start_time

        responses.append({
            "agent_id": agent_type,
            "agent_name": agent_type.replace("_", " ").title(),
            "response": result.get("response", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_time_seconds": int(round(elapsed))
        })

    return {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "sender": "CEO",
        "message": message,
        "mentioned_agents": mentioned_agents,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "sent",
        "agent_responses": responses
    }


@router.get("/chat/history", response_model=Dict[str, Any])
async def get_ceo_chat_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    agent_id: Optional[str] = Query(None, description="Filter by agent type"),
    date_from: Optional[str] = Query(None, description="Start date (ISO 8601)"),
    date_to: Optional[str] = Query(None, description="End date (ISO 8601)"),
    current_user: User = Depends(get_current_user)
):
    """
    Return CEO chat history. Chat persistence is not enabled yet.
    """
    _ = (page, page_size, agent_id, date_from, date_to, current_user)
    return {
        "messages": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    }

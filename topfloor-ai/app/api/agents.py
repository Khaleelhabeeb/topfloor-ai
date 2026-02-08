"""
Agents API - Endpoints for agent interaction
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from typing import Dict, Any, Optional
import logging
import re

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.agent import (
    AgentListResponse,
    AgentInfo,
    AgentExecutionRequest,
    AgentExecutionResponse
)
from app.schemas.session import SessionCreate
from app.orchestrator import orchestrator_manager
from app.agents import AgentRegistry, AgentFactory, AgentType
from app.adk.runner import AgentRunner
from app.services.session_service import SessionService
from app.services.agent_status_service import AgentStatusService
from app.schemas.task import TaskCreate
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    current_user: User = Depends(get_current_user)
):
    """
    List all available agents for the current user.
    
    Returns information about each agent including name, type, and description.
    """
    # Get available agents from orchestrator
    agent_infos = orchestrator_manager.list_available_agents(current_user.id)
    
    # Convert to response format
    agents = [
        AgentInfo(
            name=info["name"],
            agent_type=info["name"],  # agent_type same as name for now
            description=info["description"]
        )
        for info in agent_infos
    ]
    
    return AgentListResponse(
        agents=agents,
        total=len(agents)
    )


@router.get("/registry", response_model=Dict[str, Any])
async def get_agent_registry(
    current_user: User = Depends(get_current_user)
):
    """
    Get the complete agent registry with all agent definitions.
    
    Useful for understanding available agents and their capabilities.
    """
    agents = AgentRegistry.get_all_agents()
    
    return {
        "version": AgentRegistry.VERSION,
        "agents": [
            {
                "name": agent.name,
                "agent_type": agent.agent_type.value,
                "description": agent.description,
                "model": agent.model,
                "allowed_tools": agent.allowed_tools,
                "can_delegate": agent.can_delegate,
                "code_executor": agent.code_executor
            }
            for agent in agents
        ]
    }


@router.post("/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    request: AgentExecutionRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute an agent with a user message.
    
    This endpoint:
    1. Authenticates the user
    2. Creates or resumes a session
    3. Routes the message to the appropriate agent (orchestrator by default)
    4. Returns the agent's response
    
    **Available agent types:**
    - `orchestrator` - Routes to specialized agents (default)
    - `finance` - Financial analysis, budgeting, market research
    - `researcher` - Web research and information gathering  
    - `team_lead` - Task management and coordination
    - `data_analyst` - Data analysis and visualization
    
    For streaming responses, use the WebSocket endpoint instead.
    """
    # Determine agent type (default to orchestrator)
    agent_type = request.agent_type or "orchestrator"
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}. Valid types: orchestrator, finance, researcher, team_lead, data_analyst"
        )
    
    try:
        # Create database session for tracking
        session_data = SessionCreate(
            agent_type=agent_type,
            agent_name=agent_type,
            title=f"{agent_type.title()} Session"
        )
        db_session = SessionService.create_session(db, current_user.id, session_data)
        
        # Create services for Team Lead
        from app.services.task_service import TaskService
        from app.services.agent_status_service import AgentStatusService
        
        task_service = TaskService(db)
        agent_status_service = AgentStatusService(db)
        
        # Create the appropriate agent
        agent_type_enum = AgentType(agent_type)
        
        if agent_type_enum == AgentType.ORCHESTRATOR:
            # Full agent team with orchestrator
            agent = AgentFactory.create_agent_team(
                user_context={"user_id": current_user.id},
                task_service=task_service,
                agent_status_service=agent_status_service
            )
        elif agent_type_enum == AgentType.TEAM_LEAD:
            # Team Lead with services
            agent = AgentFactory.create_agent(
                agent_type_enum, 
                user_context={"user_id": current_user.id},
                task_service=task_service,
                agent_status_service=agent_status_service
            )
        else:
            # Single specialized agent
            agent = AgentFactory.create_agent(agent_type_enum, user_context={"user_id": current_user.id})
        
        # Create and run the agent
        runner = AgentRunner(
            agent=agent,
            session_id=db_session.session_id,
            user_id=current_user.id
        )
        
        # Execute agent with message
        logger.info(f"Executing agent {agent_type} for user {current_user.id}")
        result = await runner.run_async(
            message=request.message,
            context=request.context
        )
        
        logger.info(f"Agent execution complete. Events: {result.get('events_count', 0)}")
        
        return AgentExecutionResponse(
            session_id=db_session.session_id,
            agent_name=agent_type,
            response=result["response"],
            metadata={
                "agent_type": agent_type,
                "user_context": request.context,
                "events_count": result.get("events_count", 0)
            },
            created_at=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        error_msg = str(e)
        logger.error(f"Runtime error: {error_msg}")
        
        # Check for specific error types
        if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API rate limit exceeded. Please wait a moment and try again."
            )
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key. Please check your GOOGLE_API_KEY configuration."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent execution failed: {error_msg}"
            )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a session.
    
    Returns information about the session including active agent,
    execution status, and any errors.
    """
    from app.services.session_service import SessionService
    
    # Get session
    session = SessionService.get_session_by_id(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {
        "session_id": session.session_id,
        "agent_type": session.agent_type,
        "status": session.status.value,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }


@router.get("/status", response_model=Dict[str, Any])
async def get_all_agent_statuses(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of all agents for the current user.
    
    Returns a summary including:
    - Total number of agents
    - Count by status (available, busy, idle)
    - Total tasks in queue across all agents
    - Individual agent statuses
    """
    agent_status_service = AgentStatusService(db)
    summary = agent_status_service.get_status_summary(current_user.id)
    
    return summary


@router.get("/status/{agent_type}", response_model=Dict[str, Any])
async def get_agent_status(
    agent_type: str,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a specific agent.
    
    Returns:
    - Agent type
    - Current status (available, busy, idle)
    - Current task ID if busy
    - Number of tasks in queue
    - Last active timestamp
    """
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    agent_status_service = AgentStatusService(db)
    status_obj = agent_status_service.get_or_create_status(current_user.id, agent_type)
    
    return {
        "agent_type": status_obj.agent_type,
        "status": status_obj.status.value,
        "current_task_id": status_obj.current_task_id,
        "tasks_in_queue": status_obj.tasks_in_queue,
        "last_active_at": status_obj.last_active_at.isoformat() if status_obj.last_active_at else None,
        "updated_at": status_obj.updated_at.isoformat() if status_obj.updated_at else None
    }


# Team Lead Endpoints

@router.post("/team-lead/assign-task", response_model=Dict[str, Any])
async def team_lead_assign_task(
    task_data: TaskCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assign a task to a specific agent via the Team Lead.
    
    This endpoint allows the Team Lead to delegate tasks to other agents.
    The task is created and added to the specified agent's queue.
    
    **Request Body:**
    - agent_type: The agent to assign the task to (finance, data_analyst, researcher)
    - title: Task title
    - description: Detailed task description
    - priority: Task priority (low, medium, high, critical)
    - input_data: Optional input data for the task
    
    **Returns:**
    - Created task object with task_id, status, and metadata
    """
    from app.services.task_service import TaskService
    from app.workers.background_worker import enqueue_task
    from app.models.task import TaskStatus as TaskStatusEnum, TaskType
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(task_data.agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {task_data.agent_type}"
        )
    
    # Create task
    task_service = TaskService(db)
    try:
        task = task_service.create_task(current_user.id, task_data)
        
        queue_message = None
        if task.task_type == TaskType.BACKGROUND:
            try:
                queue_result = enqueue_task(task.id)
                if not queue_result.get("queued", True):
                    task.status = TaskStatusEnum.PENDING
                    db.commit()
                    queue_message = queue_result.get("message")
            except Exception as exc:
                task.status = TaskStatusEnum.PENDING
                db.commit()
                queue_message = str(exc)

        logger.info(f"Team Lead assigned task {task.task_id} to {task_data.agent_type}")
        
        return {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "agent_type": task.agent_type,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "message": f"Task successfully assigned to {task_data.agent_type}",
            "queue_message": queue_message
        }
    except ValueError as e:
        logger.error(f"Failed to assign task: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/team-lead/team-status", response_model=Dict[str, Any])
async def get_team_status(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of all agents in the team.
    
    This endpoint provides a comprehensive overview of:
    - Each agent's current status (available, busy, idle)
    - Number of tasks in each agent's queue
    - Current task being processed (if any)
    - Last active timestamp
    - Overall team statistics
    
    **Returns:**
    - agents: List of agent statuses
    - summary: Overall team statistics
    """
    agent_status_service = AgentStatusService(db)
    
    # Get all agent types
    agent_types = ["finance", "data_analyst", "researcher", "team_lead"]
    
    agents_status = []
    total_available = 0
    total_busy = 0
    total_idle = 0
    total_queued_tasks = 0
    
    for agent_type in agent_types:
        status_obj = agent_status_service.get_or_create_status(current_user.id, agent_type)
        
        agent_info = {
            "agent_type": status_obj.agent_type,
            "status": status_obj.status.value,
            "current_task_id": status_obj.current_task_id,
            "tasks_in_queue": status_obj.tasks_in_queue,
            "last_active_at": status_obj.last_active_at.isoformat() if status_obj.last_active_at else None
        }
        agents_status.append(agent_info)
        
        # Update counters
        if status_obj.status.value == "available":
            total_available += 1
        elif status_obj.status.value == "busy":
            total_busy += 1
        elif status_obj.status.value == "idle":
            total_idle += 1
        
        total_queued_tasks += status_obj.tasks_in_queue
    
    return {
        "agents": agents_status,
        "summary": {
            "total_agents": len(agent_types),
            "available": total_available,
            "busy": total_busy,
            "idle": total_idle,
            "total_queued_tasks": total_queued_tasks
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/team-lead/task-report", response_model=Dict[str, Any])
async def get_task_report(
    time_range: Optional[str] = "all",
    detail_level: Optional[str] = "summary",
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive task report for the team.
    
    This endpoint provides detailed insights into task execution across all agents.
    
    **Query Parameters:**
    - time_range: Filter by time (all, today, week, month) - default: all
    - detail_level: Level of detail (summary, detailed, full) - default: summary
    
    **Returns:**
    - Task statistics by status
    - Task statistics by agent
    - Task statistics by priority
    - Recent completed tasks
    - Recent failed tasks
    - Performance metrics
    """
    from app.services.task_service import TaskService
    from app.models.task import TaskStatus as TaskStatusEnum
    
    task_service = TaskService(db)
    
    # Get all tasks for the user
    all_tasks, total = task_service.get_tasks(
        user_id=current_user.id,
        sort_by="created_at",
        sort_order="desc",
        limit=1000  # Get a large number for statistics
    )
    
    # Calculate statistics
    stats_by_status = {}
    stats_by_agent = {}
    stats_by_priority = {}
    
    for task in all_tasks:
        # By status
        status_key = task.status.value
        stats_by_status[status_key] = stats_by_status.get(status_key, 0) + 1
        
        # By agent
        agent_key = task.agent_type
        if agent_key not in stats_by_agent:
            stats_by_agent[agent_key] = {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "in_progress": 0,
                "pending": 0
            }
        stats_by_agent[agent_key]["total"] += 1
        if task.status == TaskStatusEnum.COMPLETED:
            stats_by_agent[agent_key]["completed"] += 1
        elif task.status == TaskStatusEnum.FAILED:
            stats_by_agent[agent_key]["failed"] += 1
        elif task.status == TaskStatusEnum.IN_PROGRESS:
            stats_by_agent[agent_key]["in_progress"] += 1
        elif task.status == TaskStatusEnum.PENDING:
            stats_by_agent[agent_key]["pending"] += 1
        
        # By priority
        priority_key = task.priority.value
        stats_by_priority[priority_key] = stats_by_priority.get(priority_key, 0) + 1
    
    # Get recent completed tasks
    completed_tasks, _ = task_service.get_tasks(
        user_id=current_user.id,
        status=TaskStatusEnum.COMPLETED,
        sort_by="completed_at",
        sort_order="desc",
        limit=10
    )
    
    # Get recent failed tasks
    failed_tasks, _ = task_service.get_tasks(
        user_id=current_user.id,
        status=TaskStatusEnum.FAILED,
        sort_by="updated_at",
        sort_order="desc",
        limit=10
    )
    
    report = {
        "summary": {
            "total_tasks": total,
            "by_status": stats_by_status,
            "by_agent": stats_by_agent,
            "by_priority": stats_by_priority
        },
        "recent_completed": [
            {
                "task_id": task.task_id,
                "title": task.title,
                "agent_type": task.agent_type,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in completed_tasks
        ],
        "recent_failed": [
            {
                "task_id": task.task_id,
                "title": task.title,
                "agent_type": task.agent_type,
                "priority": task.priority.value,
                "error_message": task.error_message,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in failed_tasks
        ],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add detailed information if requested
    if detail_level in ["detailed", "full"]:
        # Calculate average completion time for completed tasks
        completion_times = []
        for task in all_tasks:
            if task.status == TaskStatusEnum.COMPLETED and task.started_at and task.completed_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                completion_times.append(duration)
        
        if completion_times:
            avg_completion_time = sum(completion_times) / len(completion_times)
            report["performance"] = {
                "average_completion_time_seconds": avg_completion_time,
                "total_completed_tasks": len(completion_times)
            }
    
    return report


@router.get("/{agent_type}/office", response_model=Dict[str, Any])
async def get_agent_office(
    agent_type: str,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive agent office data including status, history, and tasks.
    
    This endpoint provides all the information needed to display an agent's office:
    - Agent status and availability
    - Recent conversation history
    - Active and queued tasks
    """
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    # Get agent status
    agent_status_service = AgentStatusService(db)
    status_obj = agent_status_service.get_or_create_status(current_user.id, agent_type)
    
    # Get recent tasks
    from app.services.task_service import TaskService
    task_service = TaskService(db)
    recent_tasks, _ = task_service.get_agent_tasks(
        user_id=current_user.id,
        agent_type=agent_type,
        sort_by="created_at",
        sort_order="desc",
        limit=10
    )
    
    # Get task counts by status
    task_counts = task_service.count_tasks_by_status(
        user_id=current_user.id,
        agent_type=agent_type
    )
    
    # Get recent chat history
    from app.services.chat_service import ChatService
    chat_service = ChatService(db)
    recent_messages, _ = chat_service.get_messages_by_agent(
        user_id=current_user.id,
        agent_type=agent_type,
        sort_by="created_at",
        sort_order="desc",
        limit=20
    )
    
    return {
        "agent_type": agent_type,
        "status": {
            "status": status_obj.status.value,
            "current_task_id": status_obj.current_task_id,
            "tasks_in_queue": status_obj.tasks_in_queue,
            "last_active_at": status_obj.last_active_at.isoformat() if status_obj.last_active_at else None
        },
        "tasks": {
            "recent": [
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task in recent_tasks
            ],
            "counts": task_counts
        },
        "chat_history": {
            "recent": [
                {
                    "message_id": msg.message_id,
                    "role": msg.role.value,
                    "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in recent_messages
            ],
            "total": len(recent_messages)
        }
    }


@router.post("/{agent_type}/chat", response_model=Dict[str, Any])
async def chat_with_agent(
    agent_type: str,
    request: AgentExecutionRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with a specific agent in real-time.
    
    This endpoint:
    1. Validates the agent type
    2. Creates or resumes a session
    3. Executes the agent with the user's message
    4. Stores the conversation in chat history
    5. Returns the agent's response
    
    For streaming responses, use the WebSocket endpoint instead.
    """
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    def _is_status_inquiry(message: str) -> bool:
        normalized = message.lower()
        patterns = [
            "what are you working on",
            "what tasks are you working on",
            "what are the tasks",
            "current tasks",
            "your current tasks",
            "tasks you are working on",
            "what are you working on right now",
            "what are the task you are walking on",
            "what tasks are you walking on"
        ]
        return any(pattern in normalized for pattern in patterns)

    def _is_task_creation_request(message: str) -> bool:
        normalized = message.lower().strip()
        if normalized.endswith("?"):
            return False
        triggers = [
            "please ",
            "can you ",
            "could you ",
            "do ",
            "analyze ",
            "research ",
            "generate ",
            "create ",
            "build ",
            "prepare ",
            "summarize ",
            "report ",
            "give me ",
            "find "
        ]
        return any(normalized.startswith(trigger) for trigger in triggers)

    def _short_title(message: str) -> str:
        cleaned = re.sub(r"\s+", " ", message).strip()
        if len(cleaned) <= 80:
            return cleaned
        return cleaned[:77].rstrip() + "..."

    try:
        from app.models.session import SessionStatus
        from app.services.chat_service import ChatService

        # Reuse most recent active session for short-term memory
        sessions, _ = SessionService.list_user_sessions(
            db,
            user_id=current_user.id,
            status=SessionStatus.ACTIVE,
            agent_type=agent_type,
            page=1,
            page_size=1
        )
        if sessions:
            db_session = sessions[0]
        else:
            session_data = SessionCreate(
                agent_type=agent_type,
                agent_name=agent_type,
                title=f"{agent_type.title()} Chat"
            )
            db_session = SessionService.create_session(db, current_user.id, session_data)
        
        # Create services for Team Lead
        from app.services.task_service import TaskService
        task_service = TaskService(db)
        agent_status_service = AgentStatusService(db)
        from app.models.task import TaskStatus as TaskStatusEnum, TaskType, TaskPriority
        from app.workers.background_worker import enqueue_task

        chat_service = ChatService(db)
        recent_messages, _ = chat_service.get_messages_by_session(
            session_id=db_session.id,
            user_id=current_user.id,
            sort_by="created_at",
            sort_order="desc",
            limit=4
        )
        recent_messages = list(reversed(recent_messages))
        memory_lines = []
        for msg in recent_messages:
            role_label = "User" if msg.role.value == "user" else "Agent"
            content = msg.content.strip()
            memory_lines.append(f"{role_label}: {content}")
        memory_block = "Recent conversation:\n" + "\n".join(memory_lines) if memory_lines else ""

        if request.message and _is_status_inquiry(request.message):
            tasks, _ = task_service.get_agent_tasks(
                user_id=current_user.id,
                agent_type=agent_type,
                sort_by="updated_at",
                sort_order="desc",
                limit=20
            )
            active_statuses = {
                TaskStatusEnum.PENDING,
                TaskStatusEnum.QUEUED,
                TaskStatusEnum.IN_PROGRESS
            }
            active_tasks = [task for task in tasks if task.status in active_statuses]

            if active_tasks:
                lines = [
                    f"- {task.title} ({task.status.value})"
                    for task in active_tasks
                ]
                response_text = "Here is what I am working on:\n" + "\n".join(lines)
            else:
                response_text = "I am not working on any tasks right now."

            response_payload = {
                "session_id": db_session.session_id,
                "agent_type": agent_type,
                "response": response_text,
                "metadata": {
                    "agent_type": agent_type,
                    "intent": "status_inquiry",
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "title": task.title,
                            "status": task.status.value,
                            "priority": task.priority.value,
                            "progress": task.progress,
                            "due_date": task.due_date.isoformat() if task.due_date else None
                        }
                        for task in active_tasks
                    ]
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            chat_service.create_message(
                session_id=db_session.id,
                user_id=current_user.id,
                agent_type=agent_type,
                role="user",
                content=request.message
            )
            chat_service.create_message(
                session_id=db_session.id,
                user_id=current_user.id,
                agent_type=agent_type,
                role="agent",
                content=response_text
            )

            return response_payload

        if request.message and _is_task_creation_request(request.message):
            task_data = TaskCreate(
                agent_type=agent_type,
                title=_short_title(request.message),
                description=request.message,
                task_type=TaskType.BACKGROUND,
                priority=TaskPriority.MEDIUM,
                input_data=request.context or {},
                progress=0
            )
            task = task_service.create_task(current_user.id, task_data)

            queue_message = None
            if task.task_type == TaskType.BACKGROUND:
                try:
                    queue_result = enqueue_task(task.id)
                    if not queue_result.get("queued", True):
                        task.status = TaskStatusEnum.PENDING
                        db.commit()
                        queue_message = queue_result.get("message")
                except Exception as exc:
                    task.status = TaskStatusEnum.PENDING
                    db.commit()
                    queue_message = str(exc)

            response_text = (
                f"I created a task for that: {task.title}. "
                f"Task ID: {task.task_id}."
            )

            response_payload = {
                "session_id": db_session.session_id,
                "agent_type": agent_type,
                "response": response_text,
                "metadata": {
                    "agent_type": agent_type,
                    "intent": "task_created",
                    "task": {
                        "id": task.id,
                        "task_id": task.task_id,
                        "title": task.title,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "queue_message": queue_message
                    }
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            chat_service.create_message(
                session_id=db_session.id,
                user_id=current_user.id,
                agent_type=agent_type,
                role="user",
                content=request.message
            )
            chat_service.create_message(
                session_id=db_session.id,
                user_id=current_user.id,
                agent_type=agent_type,
                role="agent",
                content=response_text
            )

            return response_payload
        
        # Create the appropriate agent
        agent_type_enum = AgentType(agent_type)
        
        if agent_type_enum == AgentType.TEAM_LEAD:
            # Team Lead with services
            agent = AgentFactory.create_agent(
                agent_type_enum, 
                user_context={"user_id": current_user.id},
                task_service=task_service,
                agent_status_service=agent_status_service
            )
        else:
            # Single specialized agent
            agent = AgentFactory.create_agent(agent_type_enum, user_context={"user_id": current_user.id})
        
        # Create and run the agent
        runner = AgentRunner(
            agent=agent,
            session_id=db_session.session_id,
            user_id=current_user.id,
            agent_type=agent_type
        )
        
        # Execute agent with message
        logger.info(f"Chatting with agent {agent_type} for user {current_user.id}")
        context = request.context.copy() if request.context else {}
        counts = task_service.count_tasks_by_status(current_user.id, agent_type)
        context["task_context"] = {
            "agent_type": agent_type,
            "counts": counts
        }

        message = request.message
        if memory_block:
            message = f"{memory_block}\n\nUser: {request.message}"

        result = await runner.run_async(
            message=message,
            context=context
        )
        
        logger.info(f"Agent chat complete. Events: {result.get('events_count', 0)}")
        
        response_payload = {
            "session_id": db_session.session_id,
            "agent_type": agent_type,
            "response": result["response"],
            "metadata": {
                "agent_type": agent_type,
                "user_context": context,
                "events_count": result.get("events_count", 0)
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        chat_service.create_message(
            session_id=db_session.id,
            user_id=current_user.id,
            agent_type=agent_type,
            role="user",
            content=request.message
        )
        chat_service.create_message(
            session_id=db_session.id,
            user_id=current_user.id,
            agent_type=agent_type,
            role="agent",
            content=result.get("response", "")
        )

        return response_payload
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        error_msg = str(e)
        logger.error(f"Runtime error: {error_msg}")
        
        if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API rate limit exceeded. Please wait a moment and try again."
            )
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key. Please check your GOOGLE_API_KEY configuration."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent execution failed: {error_msg}"
            )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/{agent_type}/history", response_model=Dict[str, Any])
async def get_agent_history(
    agent_type: str,
    page: int = 1,
    page_size: int = 50,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history with a specific agent.
    
    Returns paginated chat messages ordered by creation time (most recent first).
    """
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {agent_type}"
        )
    
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )
    
    # Get chat history
    from app.services.chat_service import ChatService
    chat_service = ChatService(db)
    
    skip = (page - 1) * page_size
    messages, total = chat_service.get_messages_by_agent(
        user_id=current_user.id,
        agent_type=agent_type,
        sort_by="created_at",
        sort_order="desc",
        skip=skip,
        limit=page_size
    )
    
    return {
        "messages": [
            {
                "message_id": msg.message_id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "metadata": msg.message_metadata
            }
            for msg in messages
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


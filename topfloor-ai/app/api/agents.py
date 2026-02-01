"""
Agents API - Endpoints for agent interaction
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from typing import Dict, Any
import logging

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.agent import (
    AgentListResponse,
    AgentInfo,
    AgentExecutionRequest,
    AgentExecutionResponse
)
from app.orchestrator import orchestrator_manager
from app.agents import AgentRegistry, AgentFactory, AgentType
from app.adk.runner import AgentRunner
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate
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
    - `developer` - Code writing, debugging, review
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
            detail=f"Invalid agent type: {agent_type}. Valid types: orchestrator, developer, researcher, team_lead, data_analyst"
        )
    
    try:
        # Create database session for tracking
        session_data = SessionCreate(
            agent_type=agent_type,
            agent_name=agent_type,
            title=f"{agent_type.title()} Session"
        )
        db_session = SessionService.create_session(db, current_user.id, session_data)
        
        # Create the appropriate agent
        agent_type_enum = AgentType(agent_type)
        
        if agent_type_enum == AgentType.ORCHESTRATOR:
            # Full agent team with orchestrator
            agent = AgentFactory.create_agent_team(user_context={"user_id": current_user.id})
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

"""
Orchestrator Manager - Coordinates multi-agent workflows
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session as DBSession

from google.adk.agents import LlmAgent
from google.adk.runners import Runner

from app.agents import AgentFactory, AgentType
from app.adk import adk_client, session_manager, MemoryStrategy
from app.models.session import Session as DBSessionModel


class OrchestratorManager:
    """
    Manages the orchestrator agent and coordinates multi-agent workflows.
    
    Responsibilities:
    - Create orchestrator with all sub-agents
    - Manage agent delegation and routing
    - Coordinate multi-step workflows
    - Track agent interactions
    
    The orchestrator is the central hub that:
    1. Receives user requests
    2. Routes to appropriate specialized agents
    3. Manages context passing between agents
    4. Aggregates results
    """
    
    def __init__(self):
        """Initialize orchestrator manager"""
        self._orchestrators: Dict[int, LlmAgent] = {}  # user_id -> orchestrator
    
    def get_or_create_orchestrator(
        self,
        user_id: int,
        user_context: Optional[Dict[str, Any]] = None
    ) -> LlmAgent:
        """
        Get or create an orchestrator for a user.
        
        Args:
            user_id: User ID
            user_context: Optional user-specific context
            
        Returns:
            Orchestrator agent with all sub-agents
        """
        # Check cache
        if user_id in self._orchestrators:
            return self._orchestrators[user_id]
        
        # Create new orchestrator with full agent team
        context = user_context or {}
        context["user_id"] = user_id
        
        orchestrator = AgentFactory.create_agent_team(user_context=context)
        
        # Cache it
        self._orchestrators[user_id] = orchestrator
        
        return orchestrator
    
    def create_runner(
        self,
        db: DBSession,
        user_id: int,
        session_id: Optional[str] = None,
        agent_type: str = "orchestrator"
    ) -> tuple[Runner, DBSessionModel]:
        """
        Create a runner for executing agent workflows.
        
        Args:
            db: Database session
            user_id: User ID
            session_id: Optional existing session ID to resume
            agent_type: Agent type (default: orchestrator)
            
        Returns:
            Tuple of (Runner, database session)
        """
        # Get or create orchestrator
        orchestrator = self.get_or_create_orchestrator(user_id)
        
        # Get or create session
        if session_id:
            # Resume existing session
            result = session_manager.get_or_create_adk_session(
                db=db,
                session_id=session_id,
                user_id=user_id
            )
            if not result:
                raise ValueError(f"Session {session_id} not found or not active")
            db_session, adk_session = result
        else:
            # Create new session
            db_session, adk_session = session_manager.create_session(
                db=db,
                user_id=user_id,
                agent_type=agent_type,
                agent_name=agent_type,
                title=f"{agent_type.title()} Session"
            )
            
            # Initialize session state
            MemoryStrategy.initialize_session_state(
                adk_session,
                user_id=user_id,
                agent_type=agent_type
            )
        
        # Create runner
        runner = adk_client.create_runner(
            agent=orchestrator,
            app_name="topfloor-ai"
        )
        
        return runner, db_session
    
    def clear_orchestrator_cache(self, user_id: Optional[int] = None):
        """
        Clear orchestrator cache.
        
        Args:
            user_id: Optional user ID to clear specific orchestrator.
                    If None, clears all orchestrators.
        """
        if user_id is not None:
            if user_id in self._orchestrators:
                del self._orchestrators[user_id]
        else:
            self._orchestrators.clear()
    
    def get_agent_by_type(
        self,
        user_id: int,
        agent_type: AgentType
    ) -> Optional[LlmAgent]:
        """
        Get a specific agent from the orchestrator's sub-agents.
        
        Args:
            user_id: User ID
            agent_type: Type of agent to retrieve
            
        Returns:
            Agent if found, None otherwise
        """
        orchestrator = self.get_or_create_orchestrator(user_id)
        
        # Search through sub-agents
        if hasattr(orchestrator, 'sub_agents') and orchestrator.sub_agents:
            for agent in orchestrator.sub_agents:
                if hasattr(agent, 'name') and agent.name == agent_type.value:
                    return agent
        
        return None
    
    def list_available_agents(self, user_id: int) -> List[Dict[str, str]]:
        """
        List all available agents for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of agent info dictionaries
        """
        orchestrator = self.get_or_create_orchestrator(user_id)
        
        agents = []
        if hasattr(orchestrator, 'sub_agents') and orchestrator.sub_agents:
            for agent in orchestrator.sub_agents:
                agents.append({
                    "name": agent.name if hasattr(agent, 'name') else "unknown",
                    "description": agent.description if hasattr(agent, 'description') else ""
                })
        
        return agents


# Global orchestrator manager instance
orchestrator_manager = OrchestratorManager()

"""
Agent Factory - Creates ADK agents dynamically from registry definitions
"""

from typing import Dict, Any, Optional, List
from google.adk.agents import LlmAgent

from app.agents.registry import AgentRegistry, AgentType, AgentDefinition
from app.agents.base import BaseAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.tech_lead import TeamLeadAgent
from app.agents.researcher import ResearcherAgent
from app.agents.finance import FinanceAgent
from app.agents.data_analyst import DataAnalystAgent


class AgentFactory:
    """
    Factory for creating ADK agents dynamically.
    
    Responsibilities:
    - Accept agent type + user context
    - Inject correct system prompt
    - Attach session memory (in STEP 4)
    - Return ready-to-run ADK Agent instance
    
    No FastAPI logic inside the factory - pure agent construction.
    """
    
    # Map agent types to implementation classes
    _AGENT_CLASSES = {
        AgentType.ORCHESTRATOR: OrchestratorAgent,
        AgentType.TEAM_LEAD: TeamLeadAgent,
        AgentType.RESEARCHER: ResearcherAgent,
        AgentType.FINANCE: FinanceAgent,
        AgentType.DATA_ANALYST: DataAnalystAgent,
    }
    
    @classmethod
    def create_agent(
        cls,
        agent_type: AgentType,
        user_context: Optional[Dict[str, Any]] = None,
        sub_agents: Optional[List[LlmAgent]] = None,
        task_service: Optional[Any] = None,
        agent_status_service: Optional[Any] = None
    ) -> LlmAgent:
        """
        Create a single agent by type.
        
        Args:
            agent_type: Type of agent to create
            user_context: Optional user-specific context (user_id, preferences, etc.)
            sub_agents: Optional list of sub-agents (for orchestrator)
            task_service: Optional task service (for Team Lead)
            agent_status_service: Optional agent status service (for Team Lead)
            
        Returns:
            Ready-to-run ADK LlmAgent instance
            
        Raises:
            ValueError: If agent type is unknown
        """
        # Get agent definition from registry
        definition = AgentRegistry.get_agent(agent_type)
        
        # Get implementation class
        agent_class = cls._AGENT_CLASSES.get(agent_type)
        if not agent_class:
            raise ValueError(f"No implementation found for agent type: {agent_type}")
        
        # Create agent instance
        if agent_type == AgentType.ORCHESTRATOR:
            # Orchestrator needs sub-agents
            if not sub_agents:
                raise ValueError("Orchestrator requires sub_agents parameter")
            agent_instance = agent_class(definition, sub_agents, user_context)
        elif agent_type == AgentType.TEAM_LEAD:
            # Team Lead needs services for task coordination
            agent_instance = agent_class(
                definition, 
                user_context,
                task_service=task_service,
                agent_status_service=agent_status_service
            )
        else:
            agent_instance = agent_class(definition, user_context)
        
        # Build and return ADK agent
        return agent_instance.build()
    
    @classmethod
    def create_agent_team(
        cls,
        user_context: Optional[Dict[str, Any]] = None,
        task_service: Optional[Any] = None,
        agent_status_service: Optional[Any] = None
    ) -> LlmAgent:
        """
        Create a complete agent team with orchestrator and all specialists.
        This is the main entry point for creating the full multi-agent system.
        
        Args:
            user_context: Optional user-specific context
            task_service: Optional task service (for Team Lead)
            agent_status_service: Optional agent status service (for Team Lead)
            
        Returns:
            Orchestrator agent with all sub-agents configured
        """
        # Create all specialist agents first
        team_lead = cls.create_agent(
            AgentType.TEAM_LEAD, 
            user_context,
            task_service=task_service,
            agent_status_service=agent_status_service
        )
        researcher = cls.create_agent(AgentType.RESEARCHER, user_context)
        finance = cls.create_agent(AgentType.FINANCE, user_context)
        data_analyst = cls.create_agent(AgentType.DATA_ANALYST, user_context)
        
        # Create orchestrator with all specialists as sub-agents
        orchestrator = cls.create_agent(
            AgentType.ORCHESTRATOR,
            user_context,
            sub_agents=[team_lead, researcher, finance, data_analyst]
        )
        
        return orchestrator
    
    @classmethod
    def get_available_agent_types(cls) -> List[AgentType]:
        """
        Get list of all available agent types.
        
        Returns:
            List of agent types
        """
        return list(cls._AGENT_CLASSES.keys())
    
    @classmethod
    def validate_agent_type(cls, agent_type: str) -> bool:
        """
        Validate if an agent type is supported.
        
        Args:
            agent_type: Agent type string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            agent_type_enum = AgentType(agent_type)
            return agent_type_enum in cls._AGENT_CLASSES
        except ValueError:
            return False

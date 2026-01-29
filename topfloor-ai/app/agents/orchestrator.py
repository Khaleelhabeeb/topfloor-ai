"""
Orchestrator Agent - Central coordinator that routes requests to specialized agents
"""

from typing import List, Dict, Any, Optional
from google.adk.tools import FunctionTool
from google.adk.agents import LlmAgent

from app.agents.base import BaseAgent
from app.agents.registry import AgentDefinition


class OrchestratorAgent(BaseAgent):
    """
    Central hub that receives all user requests, understands intent,
    and routes to appropriate specialized agents.
    """
    
    def __init__(
        self, 
        definition: AgentDefinition, 
        sub_agents: List[LlmAgent],
        user_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize orchestrator with sub-agents
        
        Args:
            definition: Agent definition from registry
            sub_agents: List of specialized agents to coordinate
            user_context: Optional user-specific context
        """
        super().__init__(definition, user_context)
        self._sub_agents = sub_agents
    
    def build_tools(self) -> List[FunctionTool]:
        """
        Orchestrator doesn't use tools directly - it delegates to sub-agents.
        
        Returns:
            Empty list (orchestrator delegates instead of using tools)
        """
        return []
    
    def get_sub_agents(self) -> List[LlmAgent]:
        """
        Get the list of specialized agents this orchestrator can delegate to.
        
        Returns:
            List of sub-agents
        """
        return self._sub_agents

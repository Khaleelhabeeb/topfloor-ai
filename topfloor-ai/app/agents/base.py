"""
Base Agent Interface - Abstract base for all agent implementations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from app.agents.registry import AgentDefinition, AgentType


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations.
    Each agent type must implement this interface.
    """
    
    def __init__(self, definition: AgentDefinition, user_context: Optional[Dict[str, Any]] = None):
        """
        Initialize base agent
        
        Args:
            definition: Agent definition from registry
            user_context: Optional user-specific context (user_id, preferences, etc.)
        """
        self.definition = definition
        self.user_context = user_context or {}
        self._adk_agent: Optional[LlmAgent] = None
    
    @abstractmethod
    def build_tools(self) -> List[FunctionTool]:
        """
        Build the list of tools for this agent.
        Must be implemented by each agent type.
        
        Returns:
            List of ADK FunctionTool instances
        """
        pass
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Can be overridden to inject user context.
        
        Returns:
            System prompt string
        """
        return self.definition.system_prompt
    
    def get_sub_agents(self) -> List[LlmAgent]:
        """
        Get sub-agents for this agent (for orchestrator/coordinator agents).
        Override in agents that can delegate.
        
        Returns:
            List of sub-agents
        """
        return []
    
    def build(self) -> LlmAgent:
        """
        Build the ADK LlmAgent instance.
        This is the main factory method.
        
        Returns:
            Configured LlmAgent ready for execution
        """
        if self._adk_agent is not None:
            return self._adk_agent
        
        # Build tools
        tools = self.build_tools()
        
        # Get sub-agents (if any)
        sub_agents = self.get_sub_agents()
        
        # Build agent configuration
        agent_config = {
            "model": self.definition.model,
            "name": self.definition.name,
            "description": self.definition.description,
            "instruction": self.get_system_prompt(),
            "tools": tools,
        }
        
        # Only add sub_agents if there are any
        if sub_agents:
            agent_config["sub_agents"] = sub_agents
        
        # Only add code_executor if enabled (ADK will handle the actual executor)
        # For now, we'll skip code_executor until we configure it properly
        # if self.definition.code_executor:
        #     agent_config["code_executor"] = "vertexai"
        
        # Build ADK agent
        self._adk_agent = LlmAgent(**agent_config)
        
        return self._adk_agent
    
    @property
    def agent_type(self) -> AgentType:
        """Get agent type"""
        return self.definition.agent_type
    
    @property
    def name(self) -> str:
        """Get agent name"""
        return self.definition.name
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, type={self.agent_type})>"

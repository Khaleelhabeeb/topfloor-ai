"""
Tests for Agent Factory
"""

import pytest
from google.adk.agents import LlmAgent

from app.agents import AgentFactory, AgentType


class TestAgentFactory:
    """Test suite for AgentFactory"""
    
    def test_get_available_agent_types(self):
        """Test getting all available agent types"""
        agent_types = AgentFactory.get_available_agent_types()
        assert len(agent_types) == 5
        assert AgentType.ORCHESTRATOR in agent_types
        assert AgentType.TEAM_LEAD in agent_types
        assert AgentType.RESEARCHER in agent_types
        assert AgentType.FINANCE in agent_types
        assert AgentType.DATA_ANALYST in agent_types
    
    def test_validate_agent_type(self):
        """Test agent type validation"""
        assert AgentFactory.validate_agent_type("orchestrator") is True
        assert AgentFactory.validate_agent_type("team_lead") is True
        assert AgentFactory.validate_agent_type("researcher") is True
        assert AgentFactory.validate_agent_type("finance") is True
        assert AgentFactory.validate_agent_type("data_analyst") is True
        assert AgentFactory.validate_agent_type("invalid_type") is False
    
    def test_create_team_lead_agent(self):
        """Test creating a team lead agent"""
        user_context = {"user_id": "test_user"}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Verify it's an LlmAgent
        assert isinstance(agent, LlmAgent)
        assert agent.name == "team_lead"
        assert agent.description is not None
    
    def test_create_researcher_agent(self):
        """Test creating a researcher agent"""
        agent = AgentFactory.create_agent(AgentType.RESEARCHER)
        
        # Verify it's an LlmAgent
        assert isinstance(agent, LlmAgent)
        assert agent.name == "researcher"
        assert agent.description is not None
    
    def test_create_finance_agent(self):
        """Test creating a finance agent"""
        agent = AgentFactory.create_agent(AgentType.FINANCE)
        
        # Verify it's an LlmAgent
        assert isinstance(agent, LlmAgent)
        assert agent.name == "finance"
        assert agent.description is not None
    
    def test_create_data_analyst_agent(self):
        """Test creating a data analyst agent"""
        agent = AgentFactory.create_agent(AgentType.DATA_ANALYST)
        
        # Verify it's an LlmAgent
        assert isinstance(agent, LlmAgent)
        assert agent.name == "data_analyst"
        assert agent.description is not None
    
    def test_create_orchestrator_without_sub_agents_raises_error(self):
        """Test that creating orchestrator without sub-agents raises error"""
        with pytest.raises(ValueError, match="Orchestrator requires sub_agents"):
            AgentFactory.create_agent(AgentType.ORCHESTRATOR)
    
    def test_create_orchestrator_with_sub_agents(self):
        """Test creating orchestrator with sub-agents"""
        # Create sub-agents first
        team_lead = AgentFactory.create_agent(AgentType.TEAM_LEAD)
        researcher = AgentFactory.create_agent(AgentType.RESEARCHER)
        finance = AgentFactory.create_agent(AgentType.FINANCE)
        data_analyst = AgentFactory.create_agent(AgentType.DATA_ANALYST)
        
        sub_agents = [team_lead, researcher, finance, data_analyst]
        
        # Create orchestrator
        agent = AgentFactory.create_agent(
            AgentType.ORCHESTRATOR,
            sub_agents=sub_agents
        )
        
        # Verify
        assert isinstance(agent, LlmAgent)
        assert agent.name == "orchestrator"
        assert agent.description is not None
    
    def test_create_agent_team(self):
        """Test creating a complete agent team"""
        user_context = {"user_id": "test_user"}
        orchestrator = AgentFactory.create_agent_team(user_context)
        
        # Verify orchestrator was created
        assert isinstance(orchestrator, LlmAgent)
        assert orchestrator.name == "orchestrator"
    
    def test_create_unknown_agent_type_raises_error(self):
        """Test that creating unknown agent type raises error"""
        with pytest.raises(ValueError):
            AgentFactory.create_agent("unknown_type")

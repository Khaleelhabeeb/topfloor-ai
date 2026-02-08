"""
Tests for Agent Registry
"""

import pytest
from app.agents import AgentRegistry, AgentType, AgentDefinition


def test_registry_version():
    """Test registry has a version"""
    assert AgentRegistry.VERSION == "1.0.0"


def test_get_all_agents():
    """Test getting all agents from registry"""
    agents = AgentRegistry.get_all_agents()
    assert len(agents) == 5
    assert all(isinstance(agent, AgentDefinition) for agent in agents)


def test_get_agent_by_type():
    """Test getting specific agent by type"""
    orchestrator = AgentRegistry.get_agent(AgentType.ORCHESTRATOR)
    assert orchestrator.name == "orchestrator"
    assert orchestrator.agent_type == AgentType.ORCHESTRATOR
    assert orchestrator.can_delegate is True
    
    finance = AgentRegistry.get_agent(AgentType.FINANCE)
    assert finance.name == "finance"
    assert finance.code_executor is False


def test_get_unknown_agent_raises_error():
    """Test that getting unknown agent raises ValueError"""
    with pytest.raises(ValueError, match="Unknown agent type"):
        AgentRegistry.get_agent("unknown_agent")


def test_default_agents_for_user():
    """Test that users get 5 default agents"""
    default_agents = AgentRegistry.get_default_agents_for_user()
    assert len(default_agents) == 5
    assert AgentType.ORCHESTRATOR in default_agents
    assert AgentType.TEAM_LEAD in default_agents
    assert AgentType.RESEARCHER in default_agents
    assert AgentType.FINANCE in default_agents
    assert AgentType.DATA_ANALYST in default_agents


def test_validate_agent_type():
    """Test agent type validation"""
    assert AgentRegistry.validate_agent_type("orchestrator") is True
    assert AgentRegistry.validate_agent_type("finance") is True
    assert AgentRegistry.validate_agent_type("invalid_type") is False


def test_agent_definition_structure():
    """Test that all agents have required fields"""
    for agent in AgentRegistry.get_all_agents():
        assert agent.name
        assert agent.agent_type
        assert agent.description
        assert agent.system_prompt
        assert agent.model
        assert isinstance(agent.allowed_tools, list)
        assert isinstance(agent.code_executor, bool)
        assert isinstance(agent.can_delegate, bool)


def test_orchestrator_has_no_tools():
    """Test that orchestrator delegates instead of using tools"""
    orchestrator = AgentRegistry.get_agent(AgentType.ORCHESTRATOR)
    assert len(orchestrator.allowed_tools) == 0
    assert orchestrator.can_delegate is True


def test_finance_has_financial_tools():
    """Test that finance agent has financial tools"""
    finance = AgentRegistry.get_agent(AgentType.FINANCE)
    assert finance.code_executor is False
    assert "fetch_market_data" in finance.allowed_tools
    assert "analyze_bank_statement" in finance.allowed_tools
    assert "create_budget" in finance.allowed_tools


def test_researcher_has_search_tools():
    """Test that researcher has search capabilities"""
    researcher = AgentRegistry.get_agent(AgentType.RESEARCHER)
    assert "google_search" in researcher.allowed_tools

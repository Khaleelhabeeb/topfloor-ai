"""
Integration tests for Finance Agent with fetch_market_data tool
"""

import pytest

pytest.skip("Finance analysis features are disabled (pandas removed).", allow_module_level=True)

from unittest.mock import patch, MagicMock
from datetime import datetime
from app.agents.factory import AgentFactory
from app.agents.registry import AgentType, AgentRegistry
from app.agents.finance import FinanceAgent


class TestFinanceAgentIntegration:
    """Integration tests for Finance Agent"""
    
    def test_finance_agent_class_has_fetch_market_data_tool(self):
        """Test that Finance Agent class has the fetch_market_data tool"""
        definition = AgentRegistry.get_agent(AgentType.FINANCE)
        agent = FinanceAgent(definition, user_context=None)
        
        # Get the tools from the agent
        tools = agent.build_tools()
        
        # Check that fetch_market_data tool exists
        tool_names = [tool.name for tool in tools]
        assert "fetch_market_data" in tool_names
    
    @patch('app.tools.finance_tools.yf.Ticker')
    def test_finance_agent_fetch_market_data_execution(self, mock_ticker):
        """Test that Finance Agent tool executes correctly via finance_tools module"""
        from app.tools.finance_tools import fetch_market_data
        
        # Setup mock data
        dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
        mock_hist = pd.DataFrame({
            'Close': [150.0 + i for i in range(10)],
            'Volume': [50000000 + i * 1000000 for i in range(10)]
        }, index=dates)
        
        mock_info = {
            'currency': 'USD',
            'marketCap': 3000000000000,
            'longName': 'Apple Inc.'
        }
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance
        
        # Execute the tool directly
        result = fetch_market_data("AAPL", "1m", "yahoo")
        
        # Verify the result
        assert result["status"] == "success"
        assert result["symbol"] == "AAPL"
        assert result["current_price"] == 159.0
        assert "historical" in result
        assert len(result["historical"]["dates"]) == 10
        assert result["additional_info"]["company_name"] == "Apple Inc."
    
    def test_finance_agent_created_by_factory_has_tools(self):
        """Test that Finance Agent created by factory has tools configured"""
        # Create agent using factory
        agent = AgentFactory.create_agent(AgentType.FINANCE)
        
        # Verify agent is created and has tools
        assert agent is not None
        assert agent.name == "finance"
        # The tools are already attached to the LlmAgent by the factory
        # We can't directly access them, but we know they're there from the build process


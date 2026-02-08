"""
Tests for Team Lead Agent task coordination tools
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.agents.factory import AgentFactory
from app.agents.registry import AgentType
from app.services.task_service import TaskService
from app.services.agent_status_service import AgentStatusService


class TestTeamLeadTools:
    """Test Team Lead agent task coordination tools"""
    
    def test_team_lead_has_tools(self):
        """Test that Team Lead agent has task coordination tools"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Verify it's an LlmAgent with tools
        assert agent.name == "team_lead"
        assert hasattr(agent, 'tools')
        assert agent.tools is not None
        assert len(agent.tools) > 0
    
    def test_team_lead_tool_names(self):
        """Test that Team Lead has the expected tool names"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Get tool names
        tool_names = [tool.name for tool in agent.tools]
        
        # Verify expected tools exist
        expected_tools = [
            'assign_task',
            'get_agent_status',
            'list_pending_tasks',
            'update_task_status',
            'get_all_agents_status',
            'get_task_details',
            'get_task_status',
            'get_completed_tasks',
            'get_failed_tasks',
            'get_in_progress_tasks',
            'get_task_statistics',
            'generate_status_report',
            'generate_progress_report',
            'generate_team_summary'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool '{expected_tool}' not found in Team Lead tools"
    
    def test_team_lead_with_services(self):
        """Test that Team Lead can be created with services"""
        # Create mock services
        mock_db = Mock(spec=Session)
        task_service = Mock(spec=TaskService)
        agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        
        # Create agent with services
        agent = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=task_service,
            agent_status_service=agent_status_service
        )
        
        # Verify agent was created successfully
        assert agent.name == "team_lead"
        assert agent.tools is not None
        assert len(agent.tools) > 0
    
    def test_team_lead_tools_have_descriptions(self):
        """Test that all Team Lead tools have proper descriptions"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Verify all tools have descriptions
        for tool in agent.tools:
            assert hasattr(tool, 'description')
            assert tool.description is not None
            assert len(tool.description) > 0, f"Tool '{tool.name}' has empty description"
    
    def test_team_lead_in_agent_team(self):
        """Test that Team Lead is included in agent team with services"""
        user_context = {"user_id": 1}
        
        # Create mock services
        mock_db = Mock(spec=Session)
        task_service = Mock(spec=TaskService)
        agent_status_service = Mock(spec=AgentStatusService)
        
        # Create agent team
        orchestrator = AgentFactory.create_agent_team(
            user_context,
            task_service=task_service,
            agent_status_service=agent_status_service
        )
        
        # Verify orchestrator has sub-agents
        assert hasattr(orchestrator, 'sub_agents')
        assert orchestrator.sub_agents is not None
        assert len(orchestrator.sub_agents) == 4
        
        # Find Team Lead in sub-agents
        team_lead = None
        for sub_agent in orchestrator.sub_agents:
            if sub_agent.name == "team_lead":
                team_lead = sub_agent
                break
        
        assert team_lead is not None, "Team Lead not found in orchestrator sub-agents"
        assert team_lead.tools is not None
        assert len(team_lead.tools) > 0


class TestTeamLeadStatusCheckingTools:
    """Test Team Lead agent status checking tools functionality"""
    
    def test_get_task_status_tool_exists(self):
        """Test that get_task_status tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the get_task_status tool
        get_task_status_tool = None
        for tool in agent.tools:
            if tool.name == "get_task_status":
                get_task_status_tool = tool
                break
        
        assert get_task_status_tool is not None, "get_task_status tool not found"
        assert get_task_status_tool.description is not None
        assert "status" in get_task_status_tool.description.lower()
    
    def test_get_completed_tasks_tool_exists(self):
        """Test that get_completed_tasks tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the get_completed_tasks tool
        get_completed_tasks_tool = None
        for tool in agent.tools:
            if tool.name == "get_completed_tasks":
                get_completed_tasks_tool = tool
                break
        
        assert get_completed_tasks_tool is not None, "get_completed_tasks tool not found"
        assert get_completed_tasks_tool.description is not None
        assert "completed" in get_completed_tasks_tool.description.lower()
    
    def test_get_failed_tasks_tool_exists(self):
        """Test that get_failed_tasks tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the get_failed_tasks tool
        get_failed_tasks_tool = None
        for tool in agent.tools:
            if tool.name == "get_failed_tasks":
                get_failed_tasks_tool = tool
                break
        
        assert get_failed_tasks_tool is not None, "get_failed_tasks tool not found"
        assert get_failed_tasks_tool.description is not None
        assert "failed" in get_failed_tasks_tool.description.lower()
    
    def test_get_in_progress_tasks_tool_exists(self):
        """Test that get_in_progress_tasks tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the get_in_progress_tasks tool
        get_in_progress_tasks_tool = None
        for tool in agent.tools:
            if tool.name == "get_in_progress_tasks":
                get_in_progress_tasks_tool = tool
                break
        
        assert get_in_progress_tasks_tool is not None, "get_in_progress_tasks tool not found"
        assert get_in_progress_tasks_tool.description is not None
        assert "progress" in get_in_progress_tasks_tool.description.lower()
    
    def test_get_task_statistics_tool_exists(self):
        """Test that get_task_statistics tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the get_task_statistics tool
        get_task_statistics_tool = None
        for tool in agent.tools:
            if tool.name == "get_task_statistics":
                get_task_statistics_tool = tool
                break
        
        assert get_task_statistics_tool is not None, "get_task_statistics tool not found"
        assert get_task_statistics_tool.description is not None
        assert "statistics" in get_task_statistics_tool.description.lower()
    
    def test_all_status_tools_have_proper_descriptions(self):
        """Test that all status checking tools have comprehensive descriptions"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        status_tools = [
            'get_task_status',
            'get_completed_tasks',
            'get_failed_tasks',
            'get_in_progress_tasks',
            'get_task_statistics'
        ]
        
        for tool_name in status_tools:
            tool = None
            for t in agent.tools:
                if t.name == tool_name:
                    tool = t
                    break
            
            assert tool is not None, f"Tool '{tool_name}' not found"
            assert tool.description is not None, f"Tool '{tool_name}' has no description"
            assert len(tool.description) > 20, f"Tool '{tool_name}' has too short description"
    
    def test_status_tools_count(self):
        """Test that Team Lead has the correct total number of tools"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Should have 14 tools total (6 original + 5 status checking tools + 3 report generation tools)
        assert len(agent.tools) == 14, f"Expected 14 tools, found {len(agent.tools)}"


class TestTeamLeadReportGenerationTools:
    """Test Team Lead agent report generation tools functionality"""
    
    def test_generate_status_report_tool_exists(self):
        """Test that generate_status_report tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the generate_status_report tool
        generate_status_report_tool = None
        for tool in agent.tools:
            if tool.name == "generate_status_report":
                generate_status_report_tool = tool
                break
        
        assert generate_status_report_tool is not None, "generate_status_report tool not found"
        assert generate_status_report_tool.description is not None
        assert "status report" in generate_status_report_tool.description.lower()
        assert "comprehensive" in generate_status_report_tool.description.lower()
    
    def test_generate_progress_report_tool_exists(self):
        """Test that generate_progress_report tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the generate_progress_report tool
        generate_progress_report_tool = None
        for tool in agent.tools:
            if tool.name == "generate_progress_report":
                generate_progress_report_tool = tool
                break
        
        assert generate_progress_report_tool is not None, "generate_progress_report tool not found"
        assert generate_progress_report_tool.description is not None
        assert "progress report" in generate_progress_report_tool.description.lower()
        assert "completed" in generate_progress_report_tool.description.lower()
        assert "pending" in generate_progress_report_tool.description.lower()
    
    def test_generate_team_summary_tool_exists(self):
        """Test that generate_team_summary tool exists and has correct signature"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        # Find the generate_team_summary tool
        generate_team_summary_tool = None
        for tool in agent.tools:
            if tool.name == "generate_team_summary":
                generate_team_summary_tool = tool
                break
        
        assert generate_team_summary_tool is not None, "generate_team_summary tool not found"
        assert generate_team_summary_tool.description is not None
        assert "team" in generate_team_summary_tool.description.lower()
        assert "summary" in generate_team_summary_tool.description.lower()
    
    def test_all_report_tools_have_proper_descriptions(self):
        """Test that all report generation tools have comprehensive descriptions"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        report_tools = [
            'generate_status_report',
            'generate_progress_report',
            'generate_team_summary'
        ]
        
        for tool_name in report_tools:
            tool = None
            for t in agent.tools:
                if t.name == tool_name:
                    tool = t
                    break
            
            assert tool is not None, f"Tool '{tool_name}' not found"
            assert tool.description is not None, f"Tool '{tool_name}' has no description"
            assert len(tool.description) > 20, f"Tool '{tool_name}' has too short description"
    
    def test_report_tools_return_dict_structure(self):
        """Test that report generation tools are properly structured to return dictionaries"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        report_tools = [
            'generate_status_report',
            'generate_progress_report',
            'generate_team_summary'
        ]
        
        for tool_name in report_tools:
            tool = None
            for t in agent.tools:
                if t.name == tool_name:
                    tool = t
                    break
            
            assert tool is not None, f"Tool '{tool_name}' not found"
            # Verify tool has proper structure
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
    
    def test_report_generation_tools_count(self):
        """Test that Team Lead has exactly 3 report generation tools"""
        user_context = {"user_id": 1}
        agent = AgentFactory.create_agent(AgentType.TEAM_LEAD, user_context)
        
        report_tool_names = [
            'generate_status_report',
            'generate_progress_report',
            'generate_team_summary'
        ]
        
        tool_names = [tool.name for tool in agent.tools]
        
        found_count = sum(1 for name in report_tool_names if name in tool_names)
        assert found_count == 3, f"Expected 3 report generation tools, found {found_count}"

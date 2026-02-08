"""
Tests for Team Lead Agent delegation to other agents
"""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session

from app.agents.factory import AgentFactory
from app.agents.registry import AgentType, AgentRegistry
from app.services.task_service import TaskService
from app.services.agent_status_service import AgentStatusService


class TestTeamLeadDelegationCapabilities:
    """Test Team Lead agent has delegation capabilities"""
    
    def test_team_lead_has_assign_task_tool(self):
        """Test that Team Lead has assign_task tool for delegation"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Verify assign_task tool exists
        tool_names = [tool.name for tool in team_lead.tools]
        assert "assign_task" in tool_names, "Team Lead should have assign_task tool for delegation"
        
        # Find and verify the tool
        assign_task_tool = next(t for t in team_lead.tools if t.name == "assign_task")
        assert assign_task_tool is not None
        assert assign_task_tool.description is not None
        assert "assign" in assign_task_tool.description.lower()
        assert "task" in assign_task_tool.description.lower()
    
    def test_team_lead_has_agent_status_checking_tools(self):
        """Test that Team Lead has tools to check agent status before delegation"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        tool_names = [tool.name for tool in team_lead.tools]
        
        # Verify status checking tools exist
        assert "get_agent_status" in tool_names, "Team Lead should have get_agent_status tool"
        assert "get_all_agents_status" in tool_names, "Team Lead should have get_all_agents_status tool"
    
    def test_team_lead_has_task_tracking_tools(self):
        """Test that Team Lead has tools to track delegated tasks"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        tool_names = [tool.name for tool in team_lead.tools]
        
        # Verify task tracking tools exist
        assert "get_task_status" in tool_names, "Team Lead should have get_task_status tool"
        assert "get_task_details" in tool_names, "Team Lead should have get_task_details tool"
        assert "list_pending_tasks" in tool_names, "Team Lead should have list_pending_tasks tool"
        assert "update_task_status" in tool_names, "Team Lead should have update_task_status tool"
    
    def test_team_lead_can_delegate_to_all_specialist_agents(self):
        """Test that Team Lead can delegate to all specialist agents (finance, data_analyst, researcher)"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Find assign_task tool
        assign_task_tool = next(t for t in team_lead.tools if t.name == "assign_task")
        
        # Verify tool description mentions all agent types
        description = assign_task_tool.description.lower()
        
        # The tool should support delegating to these agents
        assert "finance" in description or "agent_type" in description, \
            "assign_task should support finance agent"
        assert "data_analyst" in description or "agent_type" in description, \
            "assign_task should support data_analyst agent"
        assert "researcher" in description or "agent_type" in description, \
            "assign_task should support researcher agent"
    
    def test_team_lead_supports_task_priorities(self):
        """Test that Team Lead supports different task priorities for delegation"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Find assign_task tool
        assign_task_tool = next(t for t in team_lead.tools if t.name == "assign_task")
        
        # Verify tool description mentions priority
        description = assign_task_tool.description.lower()
        assert "priority" in description, "assign_task should support task priorities"
    
    def test_team_lead_has_report_generation_tools(self):
        """Test that Team Lead has tools to generate reports on delegated work"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        tool_names = [tool.name for tool in team_lead.tools]
        
        # Verify report generation tools exist
        assert "generate_status_report" in tool_names, "Team Lead should have generate_status_report tool"
        assert "generate_progress_report" in tool_names, "Team Lead should have generate_progress_report tool"
        assert "generate_team_summary" in tool_names, "Team Lead should have generate_team_summary tool"


class TestTeamLeadInMultiAgentSystem:
    """Test Team Lead integration in multi-agent system"""
    
    def test_team_lead_is_part_of_agent_team(self):
        """Test that Team Lead is included in the agent team"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        
        # Create agent team (orchestrator with sub-agents)
        orchestrator = AgentFactory.create_agent_team(
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Verify orchestrator has sub-agents
        assert hasattr(orchestrator, 'sub_agents')
        assert orchestrator.sub_agents is not None
        assert len(orchestrator.sub_agents) == 4  # team_lead, researcher, finance, data_analyst
        
        # Find Team Lead in sub-agents
        team_lead = None
        for sub_agent in orchestrator.sub_agents:
            if sub_agent.name == "team_lead":
                team_lead = sub_agent
                break
        
        assert team_lead is not None, "Team Lead should be in orchestrator sub-agents"
        assert team_lead.tools is not None, "Team Lead should have tools"
        assert len(team_lead.tools) > 0, "Team Lead should have delegation tools"
    
    def test_team_lead_can_coordinate_with_other_agents(self):
        """Test that Team Lead can coordinate with other specialist agents"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        
        # Create agent team
        orchestrator = AgentFactory.create_agent_team(
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Get all agent names
        agent_names = [agent.name for agent in orchestrator.sub_agents]
        
        # Verify all required agents are present for coordination
        assert "team_lead" in agent_names, "Team Lead should be present"
        assert "finance" in agent_names, "Finance agent should be present for delegation"
        assert "data_analyst" in agent_names, "Data Analyst should be present for delegation"
        assert "researcher" in agent_names, "Researcher should be present for delegation"
    
    def test_team_lead_has_services_for_delegation(self):
        """Test that Team Lead is initialized with required services for delegation"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        
        # Create Team Lead with services
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Verify Team Lead was created successfully with services
        assert team_lead is not None
        assert team_lead.name == "team_lead"
        assert team_lead.tools is not None
        assert len(team_lead.tools) > 0
        
        # Verify delegation tools are present
        tool_names = [tool.name for tool in team_lead.tools]
        assert "assign_task" in tool_names
        assert "get_agent_status" in tool_names


class TestTeamLeadDelegationWorkflow:
    """Test Team Lead delegation workflow capabilities"""
    
    def test_team_lead_has_complete_delegation_workflow_tools(self):
        """Test that Team Lead has all tools needed for complete delegation workflow"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        tool_names = [tool.name for tool in team_lead.tools]
        
        # Workflow: Check status -> Assign task -> Track progress -> Generate report
        
        # Step 1: Check agent status
        assert "get_agent_status" in tool_names, "Need to check agent availability"
        assert "get_all_agents_status" in tool_names, "Need to check all agents"
        
        # Step 2: Assign task
        assert "assign_task" in tool_names, "Need to assign tasks to agents"
        
        # Step 3: Track progress
        assert "get_task_status" in tool_names, "Need to track task status"
        assert "get_task_details" in tool_names, "Need to get task details"
        assert "list_pending_tasks" in tool_names, "Need to list pending tasks"
        assert "get_in_progress_tasks" in tool_names, "Need to see in-progress tasks"
        assert "get_completed_tasks" in tool_names, "Need to see completed tasks"
        assert "get_failed_tasks" in tool_names, "Need to see failed tasks"
        
        # Step 4: Generate reports
        assert "generate_status_report" in tool_names, "Need to generate status reports"
        assert "generate_progress_report" in tool_names, "Need to generate progress reports"
        assert "generate_team_summary" in tool_names, "Need to generate team summaries"
    
    def test_team_lead_delegation_tools_have_proper_descriptions(self):
        """Test that all delegation tools have proper descriptions"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Key delegation tools
        delegation_tools = [
            "assign_task",
            "get_agent_status",
            "get_all_agents_status",
            "get_task_status",
            "list_pending_tasks"
        ]
        
        for tool_name in delegation_tools:
            tool = next((t for t in team_lead.tools if t.name == tool_name), None)
            assert tool is not None, f"Tool '{tool_name}' not found"
            assert tool.description is not None, f"Tool '{tool_name}' has no description"
            assert len(tool.description) > 20, f"Tool '{tool_name}' has too short description"
    
    def test_team_lead_system_prompt_mentions_delegation(self):
        """Test that Team Lead system prompt mentions delegation and coordination"""
        definition = AgentRegistry.get_agent(AgentType.TEAM_LEAD)
        
        system_prompt = definition.system_prompt.lower()
        
        # Verify system prompt mentions key delegation concepts
        assert "task" in system_prompt or "coordinate" in system_prompt, \
            "System prompt should mention task coordination"
        assert "agent" in system_prompt, "System prompt should mention agents"
    
    def test_team_lead_can_delegate_to_multiple_agents_simultaneously(self):
        """Test that Team Lead can manage multiple delegations"""
        mock_task_service = Mock(spec=TaskService)
        mock_agent_status_service = Mock(spec=AgentStatusService)
        
        user_context = {"user_id": 1}
        team_lead = AgentFactory.create_agent(
            AgentType.TEAM_LEAD,
            user_context,
            task_service=mock_task_service,
            agent_status_service=mock_agent_status_service
        )
        
        # Verify Team Lead has tools to manage multiple tasks
        tool_names = [tool.name for tool in team_lead.tools]
        
        # Should be able to list all pending tasks across agents
        assert "list_pending_tasks" in tool_names
        
        # Should be able to check status of all agents
        assert "get_all_agents_status" in tool_names
        
        # Should be able to get statistics across all tasks
        assert "get_task_statistics" in tool_names
        
        # Should be able to generate team-wide reports
        assert "generate_team_summary" in tool_names

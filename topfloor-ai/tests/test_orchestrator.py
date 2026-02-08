"""
Tests for Orchestrator and Multi-Agent Coordination
"""

import pytest
from sqlalchemy.orm import Session as DBSession

from app.models.user import User
from app.core.security import hash_password
from app.orchestrator import (
    OrchestratorManager,
    CollaborationContext,
    AgentTransfer,
    WorkflowCoordinator,
    ExecutionTracker,
    AgentExecutionStatus
)
from app.agents import AgentType


@pytest.fixture
def test_user(db_session: DBSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def orchestrator_manager():
    """Create a fresh orchestrator manager"""
    manager = OrchestratorManager()
    yield manager
    # Cleanup
    manager.clear_orchestrator_cache()


class TestOrchestratorManager:
    """Test suite for OrchestratorManager"""
    
    def test_get_or_create_orchestrator(
        self,
        test_user: User,
        orchestrator_manager: OrchestratorManager
    ):
        """Test creating an orchestrator"""
        orchestrator = orchestrator_manager.get_or_create_orchestrator(test_user.id)
        
        assert orchestrator is not None
        assert orchestrator.name == "orchestrator"
        assert hasattr(orchestrator, 'sub_agents')
        assert orchestrator.sub_agents is not None
        assert len(orchestrator.sub_agents) == 4  # team_lead, researcher, finance, data_analyst
    
    def test_orchestrator_caching(
        self,
        test_user: User,
        orchestrator_manager: OrchestratorManager
    ):
        """Test that orchestrator is cached"""
        orchestrator1 = orchestrator_manager.get_or_create_orchestrator(test_user.id)
        orchestrator2 = orchestrator_manager.get_or_create_orchestrator(test_user.id)
        
        # Should be the same instance
        assert orchestrator1 is orchestrator2
    
    def test_create_runner(
        self,
        db_session: DBSession,
        test_user: User,
        orchestrator_manager: OrchestratorManager
    ):
        """Test creating a runner"""
        runner, db_sess = orchestrator_manager.create_runner(
            db=db_session,
            user_id=test_user.id
        )
        
        assert runner is not None
        assert db_sess is not None
        assert db_sess.user_id == test_user.id
        assert db_sess.agent_type == "orchestrator"
    
    def test_create_runner_with_existing_session(
        self,
        db_session: DBSession,
        test_user: User,
        orchestrator_manager: OrchestratorManager
    ):
        """Test creating runner with existing session"""
        # Create initial session
        _, db_sess1 = orchestrator_manager.create_runner(
            db=db_session,
            user_id=test_user.id
        )
        
        # Resume with same session
        _, db_sess2 = orchestrator_manager.create_runner(
            db=db_session,
            user_id=test_user.id,
            session_id=db_sess1.session_id
        )
        
        assert db_sess1.id == db_sess2.id
        assert db_sess1.session_id == db_sess2.session_id
    
    def test_clear_orchestrator_cache(
        self,
        test_user: User,
        orchestrator_manager: OrchestratorManager
    ):
        """Test clearing orchestrator cache"""
        orchestrator_manager.get_or_create_orchestrator(test_user.id)
        
        # Verify it's cached
        assert test_user.id in orchestrator_manager._orchestrators
        
        # Clear cache
        orchestrator_manager.clear_orchestrator_cache(test_user.id)
        
        # Verify it's removed
        assert test_user.id not in orchestrator_manager._orchestrators
    
    def test_get_agent_by_type(
        self,
        test_user: User,
        orchestrator_manager: OrchestratorManager
    ):
        """Test getting specific agent by type"""
        agent = orchestrator_manager.get_agent_by_type(
            test_user.id,
            AgentType.FINANCE
        )
        
        assert agent is not None
        assert agent.name == "finance"
    
    def test_list_available_agents(
        self,
        test_user: User,
        orchestrator_manager: OrchestratorManager
    ):
        """Test listing available agents"""
        agents = orchestrator_manager.list_available_agents(test_user.id)
        
        assert len(agents) == 4
        agent_names = [a["name"] for a in agents]
        assert "team_lead" in agent_names
        assert "researcher" in agent_names
        assert "finance" in agent_names
        assert "data_analyst" in agent_names


class TestCollaboration:
    """Test suite for collaboration patterns"""
    
    def test_agent_transfer(self):
        """Test creating an agent transfer"""
        transfer = AgentTransfer(
            from_agent="orchestrator",
            to_agent="finance",
            reason="financial_task",
            context={"task": "analyze_portfolio"}
        )
        
        assert transfer.from_agent == "orchestrator"
        assert transfer.to_agent == "finance"
        assert transfer.reason == "financial_task"
        assert transfer.context["task"] == "analyze_portfolio"
    
    def test_collaboration_context(self):
        """Test collaboration context"""
        context = CollaborationContext()
        
        # Add transfer
        transfer = AgentTransfer("orchestrator", "finance", "financial_task")
        context.add_transfer(transfer)
        
        # Set shared data
        context.set_shared_data("project_name", "test_project")
        
        # Set agent output
        context.set_agent_output("finance", {"analysis": "portfolio_report"})
        
        # Verify
        assert len(context.transfers) == 1
        assert context.get_shared_data("project_name") == "test_project"
        assert context.get_agent_output("finance") is not None
    
    def test_transfer_chain(self):
        """Test getting transfer chain"""
        context = CollaborationContext()
        
        context.add_transfer(AgentTransfer("orchestrator", "researcher", "research"))
        context.add_transfer(AgentTransfer("researcher", "finance", "analyze"))
        context.add_transfer(AgentTransfer("finance", "data_analyst", "visualize"))
        
        chain = context.get_transfer_chain()
        
        assert chain == ["orchestrator", "researcher", "finance", "data_analyst"]
    
    def test_sequential_workflow(self):
        """Test creating sequential workflow"""
        agents = ["researcher", "finance", "data_analyst"]
        context = WorkflowCoordinator.create_sequential_workflow(
            agents,
            initial_context={"project": "test"}
        )
        
        assert len(context.transfers) == 2  # researcher->finance, finance->data_analyst
        assert context.get_shared_data("project") == "test"
    
    def test_parallel_workflow(self):
        """Test creating parallel workflow"""
        agents = ["researcher", "finance", "data_analyst"]
        context = WorkflowCoordinator.create_parallel_workflow(
            agents,
            coordinator="orchestrator"
        )
        
        assert len(context.transfers) == 3  # orchestrator->each agent
        for transfer in context.transfers:
            assert transfer.from_agent == "orchestrator"
    
    def test_merge_agent_results_combine(self):
        """Test merging agent results with combine strategy"""
        context = CollaborationContext()
        context.set_agent_output("researcher", {"findings": "data"})
        context.set_agent_output("finance", {"analysis": "portfolio_report"})
        
        merged = WorkflowCoordinator.merge_agent_results(context, "combine")
        
        assert "agents" in merged
        assert "results" in merged
        assert len(merged["agents"]) == 2
    
    def test_merge_agent_results_prioritize_first(self):
        """Test merging with prioritize_first strategy"""
        context = CollaborationContext()
        context.add_transfer(AgentTransfer("orchestrator", "researcher", "research"))
        context.add_transfer(AgentTransfer("researcher", "finance", "analyze"))
        
        context.set_agent_output("researcher", {"findings": "data"})
        context.set_agent_output("finance", {"analysis": "portfolio_report"})
        
        merged = WorkflowCoordinator.merge_agent_results(context, "prioritize_first")
        
        assert merged["primary_agent"] == "orchestrator"


class TestExecutionLifecycle:
    """Test suite for execution lifecycle tracking"""
    
    def test_execution_tracker_start(self):
        """Test starting execution tracking"""
        tracker = ExecutionTracker()
        
        execution_id = tracker.start_execution(
            agent_name="finance",
            agent_type="finance",
            user_id=1,
            session_id="sess_123",
            input_data={"task": "analyze_portfolio"}
        )
        
        assert execution_id is not None
        assert len(tracker.executions) == 1
        
        execution = tracker.get_execution(execution_id)
        assert execution is not None
        assert execution.status == AgentExecutionStatus.RUNNING
        assert execution.input_data["task"] == "analyze_portfolio"
    
    def test_execution_complete(self):
        """Test completing execution"""
        tracker = ExecutionTracker()
        
        execution_id = tracker.start_execution(
            "finance", "finance", 1, "sess_123"
        )
        
        tracker.complete_execution(
            execution_id,
            output_data={"result": "success"}
        )
        
        # Execution should be removed from active
        assert execution_id not in tracker._active_executions
        
        # But still in history
        execution = tracker.executions[0]
        assert execution.status == AgentExecutionStatus.COMPLETED
        assert execution.output_data["result"] == "success"
        assert execution.duration_seconds is not None
    
    def test_execution_fail(self):
        """Test failing execution"""
        tracker = ExecutionTracker()
        
        execution_id = tracker.start_execution(
            "finance", "finance", 1, "sess_123"
        )
        
        tracker.fail_execution(execution_id, "Test error")
        
        execution = tracker.executions[0]
        assert execution.status == AgentExecutionStatus.FAILED
        assert execution.error == "Test error"
    
    def test_get_session_executions(self):
        """Test getting executions for a session"""
        tracker = ExecutionTracker()
        
        # Create executions for different sessions
        tracker.start_execution("finance", "finance", 1, "sess_123")
        tracker.start_execution("researcher", "researcher", 1, "sess_123")
        tracker.start_execution("finance", "finance", 1, "sess_456")
        
        session_execs = tracker.get_session_executions("sess_123")
        
        assert len(session_execs) == 2
        assert all(e.session_id == "sess_123" for e in session_execs)
    
    def test_get_agent_executions(self):
        """Test getting executions for an agent"""
        tracker = ExecutionTracker()
        
        tracker.start_execution("finance", "finance", 1, "sess_123")
        tracker.start_execution("finance", "finance", 2, "sess_456")
        tracker.start_execution("researcher", "researcher", 1, "sess_789")
        
        finance_execs = tracker.get_agent_executions("finance")
        assert len(finance_execs) == 2
        
        finance_user1_execs = tracker.get_agent_executions("finance", user_id=1)
        assert len(finance_user1_execs) == 1
    
    def test_get_statistics(self):
        """Test getting execution statistics"""
        tracker = ExecutionTracker()
        
        # Create various executions
        exec1 = tracker.start_execution("finance", "finance", 1, "sess_123")
        exec2 = tracker.start_execution("finance", "finance", 1, "sess_456")
        exec3 = tracker.start_execution("researcher", "researcher", 1, "sess_789")
        
        tracker.complete_execution(exec1)
        tracker.fail_execution(exec2, "error")
        tracker.complete_execution(exec3)
        
        # Get overall stats
        stats = tracker.get_statistics()
        assert stats["total_executions"] == 3
        assert stats["completed"] == 2
        assert stats["failed"] == 1
        
        # Get agent-specific stats
        finance_stats = tracker.get_statistics(agent_name="finance")
        assert finance_stats["total_executions"] == 2
        assert finance_stats["completed"] == 1
        assert finance_stats["failed"] == 1
    
    def test_clear_old_executions(self):
        """Test clearing old executions"""
        tracker = ExecutionTracker()
        
        # Create many executions
        for i in range(150):
            tracker.start_execution(f"agent_{i}", "finance", 1, f"sess_{i}")
        
        assert len(tracker.executions) == 150
        
        # Clear old ones
        tracker.clear_old_executions(keep_last_n=100)
        
        assert len(tracker.executions) == 100

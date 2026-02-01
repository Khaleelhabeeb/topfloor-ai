"""
Unit tests for AgentStatusService
"""

import pytest
from datetime import datetime, timezone
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.agent_status import AgentStatus, AgentStatusEnum
from app.services.agent_status_service import AgentStatusService


@pytest.fixture
def agent_status_service(db_session):
    """Create an AgentStatusService instance with test database."""
    return AgentStatusService(db_session)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_task(db_session, test_user):
    """Create a test task."""
    task = Task(
        task_id="task_test123",
        user_id=test_user.id,
        agent_type="finance",
        title="Test Task",
        task_type=TaskType.BACKGROUND,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


class TestGetOrCreateStatus:
    """Tests for get_or_create_status functionality"""
    
    def test_create_new_status(self, agent_status_service, test_user):
        """Test creating a new agent status"""
        status = agent_status_service.get_or_create_status(test_user.id, "finance")
        
        assert status is not None
        assert status.id is not None
        assert status.user_id == test_user.id
        assert status.agent_type == "finance"
        assert status.status == AgentStatusEnum.AVAILABLE
        assert status.tasks_in_queue == 0
        assert status.current_task_id is None
        assert status.last_active_at is not None
        assert status.updated_at is not None
    
    def test_get_existing_status(self, agent_status_service, test_user):
        """Test getting an existing agent status"""
        # Create status
        status1 = agent_status_service.get_or_create_status(test_user.id, "finance")
        
        # Get same status
        status2 = agent_status_service.get_or_create_status(test_user.id, "finance")
        
        assert status1.id == status2.id
        assert status1.user_id == status2.user_id
        assert status1.agent_type == status2.agent_type
    
    def test_create_multiple_agent_statuses(self, agent_status_service, test_user):
        """Test creating statuses for different agents"""
        finance_status = agent_status_service.get_or_create_status(test_user.id, "finance")
        researcher_status = agent_status_service.get_or_create_status(test_user.id, "researcher")
        
        assert finance_status.id != researcher_status.id
        assert finance_status.agent_type == "finance"
        assert researcher_status.agent_type == "researcher"


class TestGetStatus:
    """Tests for retrieving agent status"""
    
    def test_get_status_existing(self, agent_status_service, test_user):
        """Test getting an existing status"""
        created_status = agent_status_service.get_or_create_status(test_user.id, "finance")
        
        retrieved_status = agent_status_service.get_status(test_user.id, "finance")
        
        assert retrieved_status is not None
        assert retrieved_status.id == created_status.id
    
    def test_get_status_nonexistent(self, agent_status_service, test_user):
        """Test getting a non-existent status returns None"""
        status = agent_status_service.get_status(test_user.id, "finance")
        
        assert status is None
    
    def test_get_status_by_id(self, agent_status_service, test_user):
        """Test getting status by database ID"""
        created_status = agent_status_service.get_or_create_status(test_user.id, "finance")
        
        retrieved_status = agent_status_service.get_status_by_id(created_status.id)
        
        assert retrieved_status is not None
        assert retrieved_status.id == created_status.id
    
    def test_get_status_by_id_with_user_filter(self, agent_status_service, test_user):
        """Test getting status by ID with user filter"""
        created_status = agent_status_service.get_or_create_status(test_user.id, "finance")
        
        retrieved_status = agent_status_service.get_status_by_id(created_status.id, user_id=test_user.id)
        
        assert retrieved_status is not None
    
    def test_get_status_by_id_wrong_user_returns_none(self, agent_status_service, test_user):
        """Test getting status with wrong user_id returns None"""
        created_status = agent_status_service.get_or_create_status(test_user.id, "finance")
        
        retrieved_status = agent_status_service.get_status_by_id(created_status.id, user_id=99999)
        
        assert retrieved_status is None


class TestGetAllStatuses:
    """Tests for getting all agent statuses"""
    
    def test_get_all_statuses_empty(self, agent_status_service, test_user):
        """Test getting all statuses when none exist"""
        statuses = agent_status_service.get_all_statuses(test_user.id)
        
        assert statuses == []
    
    def test_get_all_statuses_multiple(self, agent_status_service, test_user):
        """Test getting all statuses for a user"""
        agent_status_service.get_or_create_status(test_user.id, "finance")
        agent_status_service.get_or_create_status(test_user.id, "researcher")
        agent_status_service.get_or_create_status(test_user.id, "data_analyst")
        
        statuses = agent_status_service.get_all_statuses(test_user.id)
        
        assert len(statuses) == 3
        agent_types = {s.agent_type for s in statuses}
        assert agent_types == {"finance", "researcher", "data_analyst"}


class TestSetStatus:
    """Tests for setting agent status"""
    
    def test_set_status_to_busy(self, agent_status_service, test_user, test_task):
        """Test setting agent status to busy"""
        status = agent_status_service.set_status(
            test_user.id,
            "finance",
            AgentStatusEnum.BUSY,
            current_task_id=test_task.id
        )
        
        assert status.status == AgentStatusEnum.BUSY
        assert status.current_task_id == test_task.id
    
    def test_set_status_to_available(self, agent_status_service, test_user):
        """Test setting agent status to available"""
        status = agent_status_service.set_status(
            test_user.id,
            "finance",
            AgentStatusEnum.AVAILABLE
        )
        
        assert status.status == AgentStatusEnum.AVAILABLE
        assert status.current_task_id is None
    
    def test_set_status_to_idle(self, agent_status_service, test_user):
        """Test setting agent status to idle"""
        status = agent_status_service.set_status(
            test_user.id,
            "finance",
            AgentStatusEnum.IDLE
        )
        
        assert status.status == AgentStatusEnum.IDLE
    
    def test_set_status_updates_timestamps(self, agent_status_service, test_user):
        """Test that setting status updates timestamps"""
        status = agent_status_service.get_or_create_status(test_user.id, "finance")
        original_updated_at = status.updated_at
        
        # Wait a moment and update status
        import time
        time.sleep(0.01)
        
        updated_status = agent_status_service.set_status(
            test_user.id,
            "finance",
            AgentStatusEnum.BUSY
        )
        
        assert updated_status.updated_at > original_updated_at
        assert updated_status.last_active_at is not None


class TestConvenienceMethods:
    """Tests for convenience methods"""
    
    def test_set_available(self, agent_status_service, test_user):
        """Test set_available convenience method"""
        status = agent_status_service.set_available(test_user.id, "finance")
        
        assert status.status == AgentStatusEnum.AVAILABLE
        assert status.current_task_id is None
    
    def test_set_busy(self, agent_status_service, test_user, test_task):
        """Test set_busy convenience method"""
        status = agent_status_service.set_busy(test_user.id, "finance", test_task.id)
        
        assert status.status == AgentStatusEnum.BUSY
        assert status.current_task_id == test_task.id
    
    def test_set_idle(self, agent_status_service, test_user):
        """Test set_idle convenience method"""
        status = agent_status_service.set_idle(test_user.id, "finance")
        
        assert status.status == AgentStatusEnum.IDLE
        assert status.current_task_id is None


class TestQueueManagement:
    """Tests for queue management functionality"""
    
    def test_update_queue_length(self, agent_status_service, test_user):
        """Test updating queue length"""
        status = agent_status_service.update_queue_length(test_user.id, "finance", 5)
        
        assert status.tasks_in_queue == 5
    
    def test_increment_queue(self, agent_status_service, test_user):
        """Test incrementing queue length"""
        agent_status_service.get_or_create_status(test_user.id, "finance")
        
        status = agent_status_service.increment_queue(test_user.id, "finance")
        assert status.tasks_in_queue == 1
        
        status = agent_status_service.increment_queue(test_user.id, "finance")
        assert status.tasks_in_queue == 2
    
    def test_decrement_queue(self, agent_status_service, test_user):
        """Test decrementing queue length"""
        agent_status_service.update_queue_length(test_user.id, "finance", 3)
        
        status = agent_status_service.decrement_queue(test_user.id, "finance")
        assert status.tasks_in_queue == 2
        
        status = agent_status_service.decrement_queue(test_user.id, "finance")
        assert status.tasks_in_queue == 1
    
    def test_decrement_queue_does_not_go_below_zero(self, agent_status_service, test_user):
        """Test that decrementing queue doesn't go below 0"""
        agent_status_service.get_or_create_status(test_user.id, "finance")
        
        status = agent_status_service.decrement_queue(test_user.id, "finance")
        assert status.tasks_in_queue == 0
        
        # Try to decrement again
        status = agent_status_service.decrement_queue(test_user.id, "finance")
        assert status.tasks_in_queue == 0


class TestActivityTracking:
    """Tests for activity tracking"""
    
    def test_update_last_active(self, agent_status_service, test_user):
        """Test updating last active timestamp"""
        status = agent_status_service.get_or_create_status(test_user.id, "finance")
        original_last_active = status.last_active_at
        
        import time
        time.sleep(0.01)
        
        updated_status = agent_status_service.update_last_active(test_user.id, "finance")
        
        assert updated_status.last_active_at > original_last_active


class TestStatusChecks:
    """Tests for status checking methods"""
    
    def test_is_available_when_available(self, agent_status_service, test_user):
        """Test is_available returns True when agent is available"""
        agent_status_service.set_available(test_user.id, "finance")
        
        assert agent_status_service.is_available(test_user.id, "finance") is True
    
    def test_is_available_when_busy(self, agent_status_service, test_user, test_task):
        """Test is_available returns False when agent is busy"""
        agent_status_service.set_busy(test_user.id, "finance", test_task.id)
        
        assert agent_status_service.is_available(test_user.id, "finance") is False
    
    def test_is_available_when_no_status_exists(self, agent_status_service, test_user):
        """Test is_available returns True when no status exists"""
        assert agent_status_service.is_available(test_user.id, "finance") is True
    
    def test_is_busy_when_busy(self, agent_status_service, test_user, test_task):
        """Test is_busy returns True when agent is busy"""
        agent_status_service.set_busy(test_user.id, "finance", test_task.id)
        
        assert agent_status_service.is_busy(test_user.id, "finance") is True
    
    def test_is_busy_when_available(self, agent_status_service, test_user):
        """Test is_busy returns False when agent is available"""
        agent_status_service.set_available(test_user.id, "finance")
        
        assert agent_status_service.is_busy(test_user.id, "finance") is False
    
    def test_get_current_task(self, agent_status_service, test_user, test_task):
        """Test getting current task ID"""
        agent_status_service.set_busy(test_user.id, "finance", test_task.id)
        
        current_task_id = agent_status_service.get_current_task(test_user.id, "finance")
        
        assert current_task_id == test_task.id
    
    def test_get_current_task_when_available(self, agent_status_service, test_user):
        """Test getting current task when agent is available"""
        agent_status_service.set_available(test_user.id, "finance")
        
        current_task_id = agent_status_service.get_current_task(test_user.id, "finance")
        
        assert current_task_id is None
    
    def test_get_queue_length(self, agent_status_service, test_user):
        """Test getting queue length"""
        agent_status_service.update_queue_length(test_user.id, "finance", 5)
        
        queue_length = agent_status_service.get_queue_length(test_user.id, "finance")
        
        assert queue_length == 5
    
    def test_get_queue_length_when_no_status(self, agent_status_service, test_user):
        """Test getting queue length when no status exists"""
        queue_length = agent_status_service.get_queue_length(test_user.id, "finance")
        
        assert queue_length == 0


class TestFilteringMethods:
    """Tests for filtering agent statuses"""
    
    def test_get_available_agents(self, agent_status_service, test_user, test_task):
        """Test getting all available agents"""
        agent_status_service.set_available(test_user.id, "finance")
        agent_status_service.set_busy(test_user.id, "researcher", test_task.id)
        agent_status_service.set_available(test_user.id, "data_analyst")
        
        available_agents = agent_status_service.get_available_agents(test_user.id)
        
        assert len(available_agents) == 2
        agent_types = {a.agent_type for a in available_agents}
        assert agent_types == {"finance", "data_analyst"}
    
    def test_get_busy_agents(self, agent_status_service, test_user, test_task):
        """Test getting all busy agents"""
        agent_status_service.set_available(test_user.id, "finance")
        agent_status_service.set_busy(test_user.id, "researcher", test_task.id)
        agent_status_service.set_busy(test_user.id, "data_analyst", test_task.id)
        
        busy_agents = agent_status_service.get_busy_agents(test_user.id)
        
        assert len(busy_agents) == 2
        agent_types = {a.agent_type for a in busy_agents}
        assert agent_types == {"researcher", "data_analyst"}


class TestStatusSummary:
    """Tests for status summary functionality"""
    
    def test_get_status_summary(self, agent_status_service, test_user, test_task):
        """Test getting status summary"""
        agent_status_service.set_available(test_user.id, "finance")
        agent_status_service.set_busy(test_user.id, "researcher", test_task.id)
        agent_status_service.set_idle(test_user.id, "data_analyst")
        agent_status_service.update_queue_length(test_user.id, "finance", 2)
        agent_status_service.update_queue_length(test_user.id, "researcher", 3)
        
        summary = agent_status_service.get_status_summary(test_user.id)
        
        assert summary["total_agents"] == 3
        assert summary["available"] == 1
        assert summary["busy"] == 1
        assert summary["idle"] == 1
        assert summary["total_tasks_in_queue"] == 5
        assert len(summary["agents"]) == 3
    
    def test_get_status_summary_empty(self, agent_status_service, test_user):
        """Test getting status summary when no agents exist"""
        summary = agent_status_service.get_status_summary(test_user.id)
        
        assert summary["total_agents"] == 0
        assert summary["available"] == 0
        assert summary["busy"] == 0
        assert summary["idle"] == 0
        assert summary["total_tasks_in_queue"] == 0
        assert summary["agents"] == []


class TestDeleteAndReset:
    """Tests for deleting and resetting status"""
    
    def test_delete_status(self, agent_status_service, test_user):
        """Test deleting agent status"""
        agent_status_service.get_or_create_status(test_user.id, "finance")
        
        result = agent_status_service.delete_status(test_user.id, "finance")
        
        assert result is True
        
        # Verify status is deleted
        status = agent_status_service.get_status(test_user.id, "finance")
        assert status is None
    
    def test_delete_status_nonexistent(self, agent_status_service, test_user):
        """Test deleting non-existent status returns False"""
        result = agent_status_service.delete_status(test_user.id, "finance")
        
        assert result is False
    
    def test_reset_status(self, agent_status_service, test_user, test_task):
        """Test resetting agent status to defaults"""
        # Set status to busy with queue
        agent_status_service.set_busy(test_user.id, "finance", test_task.id)
        agent_status_service.update_queue_length(test_user.id, "finance", 5)
        
        # Reset status
        reset_status = agent_status_service.reset_status(test_user.id, "finance")
        
        assert reset_status.status == AgentStatusEnum.AVAILABLE
        assert reset_status.current_task_id is None
        assert reset_status.tasks_in_queue == 0

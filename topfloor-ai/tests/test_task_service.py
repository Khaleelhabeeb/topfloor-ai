"""
Unit tests for TaskService
"""

import pytest
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


@pytest.fixture
def task_service(db_session):
    """Create a TaskService instance with test database."""
    return TaskService(db_session)


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
def sample_task_data():
    """Sample task data for testing."""
    return TaskCreate(
        title="Test Task",
        description="This is a test task",
        agent_type="finance",
        task_type=TaskType.BACKGROUND,
        priority=TaskPriority.MEDIUM,
        input_data={"key": "value"}
    )


class TestCreateTask:
    """Tests for task creation functionality"""
    
    def test_create_task_success(self, task_service, test_user, sample_task_data):
        """Test successful task creation"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        assert task is not None
        assert task.id is not None
        assert task.task_id is not None
        assert task.task_id.startswith("task_")
        assert task.user_id == test_user.id
        assert task.title == sample_task_data.title
        assert task.description == sample_task_data.description
        assert task.agent_type == sample_task_data.agent_type
        assert task.task_type == sample_task_data.task_type
        assert task.priority == sample_task_data.priority
        assert task.status == TaskStatus.PENDING
        assert task.input_data == sample_task_data.input_data
        assert task.created_at is not None
    
    def test_create_task_generates_unique_task_id(self, task_service, test_user, sample_task_data):
        """Test that each task gets a unique task_id"""
        task1 = task_service.create_task(test_user.id, sample_task_data)
        task2 = task_service.create_task(test_user.id, sample_task_data)
        
        assert task1.task_id != task2.task_id
    
    def test_create_task_sets_default_status_to_pending(self, task_service, test_user, sample_task_data):
        """Test that new tasks default to PENDING status"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        assert task.status == TaskStatus.PENDING
    
    def test_create_task_with_different_priorities(self, task_service, test_user):
        """Test creating tasks with different priority levels"""
        for priority in TaskPriority:
            task_data = TaskCreate(
                title=f"Task with {priority.value} priority",
                agent_type="finance",
                priority=priority
            )
            task = task_service.create_task(test_user.id, task_data)
            
            assert task.priority == priority
    
    def test_create_task_with_different_types(self, task_service, test_user):
        """Test creating tasks with different types"""
        for task_type in TaskType:
            task_data = TaskCreate(
                title=f"Task of type {task_type.value}",
                agent_type="finance",
                task_type=task_type
            )
            task = task_service.create_task(test_user.id, task_data)
            
            assert task.task_type == task_type
    
    def test_create_task_without_optional_fields(self, task_service, test_user):
        """Test creating task with only required fields"""
        task_data = TaskCreate(
            title="Minimal Task",
            agent_type="finance"
        )
        task = task_service.create_task(test_user.id, task_data)
        
        assert task is not None
        assert task.description is None
        assert task.input_data is None


class TestGetTaskById:
    """Tests for retrieving tasks by ID"""
    
    def test_get_task_by_id_existing_task(self, task_service, test_user, sample_task_data):
        """Test retrieving an existing task by database ID"""
        created_task = task_service.create_task(test_user.id, sample_task_data)
        
        retrieved_task = task_service.get_task_by_id(created_task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title
    
    def test_get_task_by_id_with_user_filter(self, task_service, test_user, sample_task_data):
        """Test retrieving task with user_id filter"""
        created_task = task_service.create_task(test_user.id, sample_task_data)
        
        retrieved_task = task_service.get_task_by_id(created_task.id, user_id=test_user.id)
        
        assert retrieved_task is not None
        assert retrieved_task.user_id == test_user.id
    
    def test_get_task_by_id_wrong_user_returns_none(self, task_service, test_user, sample_task_data):
        """Test that retrieving task with wrong user_id returns None"""
        created_task = task_service.create_task(test_user.id, sample_task_data)
        
        retrieved_task = task_service.get_task_by_id(created_task.id, user_id=99999)
        
        assert retrieved_task is None
    
    def test_get_task_by_id_nonexistent_task(self, task_service):
        """Test retrieving a non-existent task returns None"""
        retrieved_task = task_service.get_task_by_id(99999)
        
        assert retrieved_task is None


class TestGetTaskByTaskId:
    """Tests for retrieving tasks by task_id string"""
    
    def test_get_task_by_task_id_existing_task(self, task_service, test_user, sample_task_data):
        """Test retrieving an existing task by task_id string"""
        created_task = task_service.create_task(test_user.id, sample_task_data)
        
        retrieved_task = task_service.get_task_by_task_id(created_task.task_id)
        
        assert retrieved_task is not None
        assert retrieved_task.task_id == created_task.task_id
        assert retrieved_task.id == created_task.id
    
    def test_get_task_by_task_id_with_user_filter(self, task_service, test_user, sample_task_data):
        """Test retrieving task by task_id with user filter"""
        created_task = task_service.create_task(test_user.id, sample_task_data)
        
        retrieved_task = task_service.get_task_by_task_id(created_task.task_id, user_id=test_user.id)
        
        assert retrieved_task is not None
    
    def test_get_task_by_task_id_nonexistent_task(self, task_service):
        """Test retrieving non-existent task by task_id returns None"""
        retrieved_task = task_service.get_task_by_task_id("task_nonexistent")
        
        assert retrieved_task is None


class TestGetTasks:
    """Tests for listing tasks with filters"""
    
    def test_get_tasks_returns_user_tasks(self, task_service, test_user, sample_task_data):
        """Test getting all tasks for a user"""
        task1 = task_service.create_task(test_user.id, sample_task_data)
        task2 = task_service.create_task(test_user.id, sample_task_data)
        
        tasks, total = task_service.get_tasks(test_user.id)
        
        assert total == 2
        assert len(tasks) == 2
        assert any(t.id == task1.id for t in tasks)
        assert any(t.id == task2.id for t in tasks)
    
    def test_get_tasks_filter_by_agent_type(self, task_service, test_user):
        """Test filtering tasks by agent type"""
        finance_task = task_service.create_task(test_user.id, TaskCreate(
            title="Finance Task",
            agent_type="finance"
        ))
        researcher_task = task_service.create_task(test_user.id, TaskCreate(
            title="Research Task",
            agent_type="researcher"
        ))
        
        tasks, total = task_service.get_tasks(test_user.id, agent_type="finance")
        
        assert total == 1
        assert len(tasks) == 1
        assert tasks[0].id == finance_task.id
    
    def test_get_tasks_filter_by_status(self, task_service, test_user, sample_task_data):
        """Test filtering tasks by status"""
        task = task_service.create_task(test_user.id, sample_task_data)
        task_service.update_task_status(task.id, test_user.id, TaskStatus.COMPLETED)
        
        pending_tasks, pending_total = task_service.get_tasks(test_user.id, status=TaskStatus.PENDING)
        completed_tasks, completed_total = task_service.get_tasks(test_user.id, status=TaskStatus.COMPLETED)
        
        assert pending_total == 0
        assert completed_total == 1
    
    def test_get_tasks_filter_by_task_type(self, task_service, test_user):
        """Test filtering tasks by task type"""
        chat_task = task_service.create_task(test_user.id, TaskCreate(
            title="Chat Task",
            agent_type="finance",
            task_type=TaskType.CHAT
        ))
        bg_task = task_service.create_task(test_user.id, TaskCreate(
            title="Background Task",
            agent_type="finance",
            task_type=TaskType.BACKGROUND
        ))
        
        tasks, total = task_service.get_tasks(test_user.id, task_type=TaskType.CHAT)
        
        assert total == 1
        assert tasks[0].id == chat_task.id
    
    def test_get_tasks_filter_by_priority(self, task_service, test_user):
        """Test filtering tasks by priority"""
        high_task = task_service.create_task(test_user.id, TaskCreate(
            title="High Priority Task",
            agent_type="finance",
            priority=TaskPriority.HIGH
        ))
        low_task = task_service.create_task(test_user.id, TaskCreate(
            title="Low Priority Task",
            agent_type="finance",
            priority=TaskPriority.LOW
        ))
        
        tasks, total = task_service.get_tasks(test_user.id, priority=TaskPriority.HIGH)
        
        assert total == 1
        assert tasks[0].id == high_task.id
    
    def test_get_tasks_pagination(self, task_service, test_user, sample_task_data):
        """Test pagination of task list"""
        # Create 5 tasks
        for i in range(5):
            task_service.create_task(test_user.id, sample_task_data)
        
        # Get first page (2 items)
        page1_tasks, total = task_service.get_tasks(test_user.id, skip=0, limit=2)
        
        assert total == 5
        assert len(page1_tasks) == 2
        
        # Get second page (2 items)
        page2_tasks, _ = task_service.get_tasks(test_user.id, skip=2, limit=2)
        
        assert len(page2_tasks) == 2
        assert page1_tasks[0].id != page2_tasks[0].id
    
    def test_get_tasks_ordered_by_created_at_desc(self, task_service, test_user, sample_task_data):
        """Test that tasks are ordered by creation time (newest first)"""
        task1 = task_service.create_task(test_user.id, sample_task_data)
        task2 = task_service.create_task(test_user.id, sample_task_data)
        task3 = task_service.create_task(test_user.id, sample_task_data)
        
        tasks, _ = task_service.get_tasks(test_user.id)
        
        # Newest should be first
        assert tasks[0].id == task3.id
        assert tasks[1].id == task2.id
        assert tasks[2].id == task1.id


class TestUpdateTask:
    """Tests for updating tasks"""
    
    def test_update_task_title(self, task_service, test_user, sample_task_data):
        """Test updating task title"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        update_data = TaskUpdate(title="Updated Title")
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task is not None
        assert updated_task.title == "Updated Title"
    
    def test_update_task_status(self, task_service, test_user, sample_task_data):
        """Test updating task status"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.status == TaskStatus.IN_PROGRESS
    
    def test_update_task_sets_started_at_when_in_progress(self, task_service, test_user, sample_task_data):
        """Test that started_at is set when status changes to IN_PROGRESS"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        assert task.started_at is None
        
        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.started_at is not None
    
    def test_update_task_sets_completed_at_when_completed(self, task_service, test_user, sample_task_data):
        """Test that completed_at is set when status changes to COMPLETED"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        assert task.completed_at is None
        
        update_data = TaskUpdate(status=TaskStatus.COMPLETED)
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.completed_at is not None
    
    def test_update_task_sets_completed_at_when_failed(self, task_service, test_user, sample_task_data):
        """Test that completed_at is set when status changes to FAILED"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        update_data = TaskUpdate(status=TaskStatus.FAILED, error_message="Test error")
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.completed_at is not None
        assert updated_task.error_message == "Test error"
    
    def test_update_task_result_data(self, task_service, test_user, sample_task_data):
        """Test updating task result data"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        result_data = {"output": "test result", "metrics": {"count": 42}}
        update_data = TaskUpdate(result_data=result_data)
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.result_data == result_data
    
    def test_update_task_multiple_fields(self, task_service, test_user, sample_task_data):
        """Test updating multiple fields at once"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        update_data = TaskUpdate(
            title="New Title",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            result_data={"result": "success"}
        )
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.title == "New Title"
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.priority == TaskPriority.HIGH
        assert updated_task.result_data == {"result": "success"}
    
    def test_update_task_wrong_user_returns_none(self, task_service, test_user, sample_task_data):
        """Test that updating task with wrong user_id returns None"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        update_data = TaskUpdate(title="Updated Title")
        updated_task = task_service.update_task(task.id, 99999, update_data)
        
        assert updated_task is None
    
    def test_update_task_nonexistent_task_returns_none(self, task_service, test_user):
        """Test that updating non-existent task returns None"""
        update_data = TaskUpdate(title="Updated Title")
        updated_task = task_service.update_task(99999, test_user.id, update_data)
        
        assert updated_task is None


class TestDeleteTask:
    """Tests for deleting tasks"""
    
    def test_delete_task_success(self, task_service, test_user, sample_task_data):
        """Test successful task deletion"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        result = task_service.delete_task(task.id, test_user.id)
        
        assert result is True
        
        # Verify task is deleted
        deleted_task = task_service.get_task_by_id(task.id)
        assert deleted_task is None
    
    def test_delete_task_wrong_user_returns_false(self, task_service, test_user, sample_task_data):
        """Test that deleting task with wrong user_id returns False"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        result = task_service.delete_task(task.id, 99999)
        
        assert result is False
        
        # Verify task still exists
        existing_task = task_service.get_task_by_id(task.id)
        assert existing_task is not None
    
    def test_delete_task_nonexistent_task_returns_false(self, task_service, test_user):
        """Test that deleting non-existent task returns False"""
        result = task_service.delete_task(99999, test_user.id)
        
        assert result is False


class TestConvenienceMethods:
    """Tests for convenience methods"""
    
    def test_update_task_status_convenience_method(self, task_service, test_user, sample_task_data):
        """Test update_task_status convenience method"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        updated_task = task_service.update_task_status(
            task.id,
            test_user.id,
            TaskStatus.COMPLETED
        )
        
        assert updated_task.status == TaskStatus.COMPLETED
    
    def test_update_task_status_with_error_message(self, task_service, test_user, sample_task_data):
        """Test update_task_status with error message"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        updated_task = task_service.update_task_status(
            task.id,
            test_user.id,
            TaskStatus.FAILED,
            error_message="Something went wrong"
        )
        
        assert updated_task.status == TaskStatus.FAILED
        assert updated_task.error_message == "Something went wrong"
    
    def test_update_task_result_convenience_method(self, task_service, test_user, sample_task_data):
        """Test update_task_result convenience method"""
        task = task_service.create_task(test_user.id, sample_task_data)
        
        result_data = {"output": "test result"}
        updated_task = task_service.update_task_result(
            task.id,
            test_user.id,
            result_data
        )
        
        assert updated_task.result_data == result_data
    
    def test_get_agent_tasks_convenience_method(self, task_service, test_user):
        """Test get_agent_tasks convenience method"""
        finance_task = task_service.create_task(test_user.id, TaskCreate(
            title="Finance Task",
            agent_type="finance"
        ))
        researcher_task = task_service.create_task(test_user.id, TaskCreate(
            title="Research Task",
            agent_type="researcher"
        ))
        
        tasks, total = task_service.get_agent_tasks(test_user.id, "finance")
        
        assert total == 1
        assert tasks[0].id == finance_task.id


class TestGetPendingTasks:
    """Tests for getting pending tasks"""
    
    def test_get_pending_tasks_returns_only_pending(self, task_service, test_user, sample_task_data):
        """Test that get_pending_tasks returns only pending tasks"""
        pending_task = task_service.create_task(test_user.id, sample_task_data)
        completed_task = task_service.create_task(test_user.id, sample_task_data)
        task_service.update_task_status(completed_task.id, test_user.id, TaskStatus.COMPLETED)
        
        pending_tasks = task_service.get_pending_tasks(test_user.id)
        
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == pending_task.id
    
    def test_get_pending_tasks_ordered_by_priority(self, task_service, test_user):
        """Test that pending tasks are ordered by priority"""
        low_task = task_service.create_task(test_user.id, TaskCreate(
            title="Low Priority",
            agent_type="finance",
            priority=TaskPriority.LOW
        ))
        critical_task = task_service.create_task(test_user.id, TaskCreate(
            title="Critical Priority",
            agent_type="finance",
            priority=TaskPriority.CRITICAL
        ))
        medium_task = task_service.create_task(test_user.id, TaskCreate(
            title="Medium Priority",
            agent_type="finance",
            priority=TaskPriority.MEDIUM
        ))
        
        pending_tasks = task_service.get_pending_tasks(test_user.id)
        
        # Should be ordered: critical, medium, low
        assert pending_tasks[0].id == critical_task.id
        assert pending_tasks[1].id == medium_task.id
        assert pending_tasks[2].id == low_task.id
    
    def test_get_pending_tasks_filter_by_agent(self, task_service, test_user):
        """Test filtering pending tasks by agent type"""
        finance_task = task_service.create_task(test_user.id, TaskCreate(
            title="Finance Task",
            agent_type="finance"
        ))
        researcher_task = task_service.create_task(test_user.id, TaskCreate(
            title="Research Task",
            agent_type="researcher"
        ))
        
        pending_tasks = task_service.get_pending_tasks(test_user.id, agent_type="finance")
        
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == finance_task.id


class TestCountTasksByStatus:
    """Tests for counting tasks by status"""
    
    def test_count_tasks_by_status(self, task_service, test_user, sample_task_data):
        """Test counting tasks by status"""
        # Create tasks with different statuses
        task1 = task_service.create_task(test_user.id, sample_task_data)
        task2 = task_service.create_task(test_user.id, sample_task_data)
        task3 = task_service.create_task(test_user.id, sample_task_data)
        
        task_service.update_task_status(task2.id, test_user.id, TaskStatus.COMPLETED)
        task_service.update_task_status(task3.id, test_user.id, TaskStatus.FAILED)
        
        counts = task_service.count_tasks_by_status(test_user.id)
        
        assert counts["pending"] == 1
        assert counts["completed"] == 1
        assert counts["failed"] == 1
        assert counts["in_progress"] == 0
    
    def test_count_tasks_by_status_filter_by_agent(self, task_service, test_user):
        """Test counting tasks by status for specific agent"""
        finance_task = task_service.create_task(test_user.id, TaskCreate(
            title="Finance Task",
            agent_type="finance"
        ))
        researcher_task = task_service.create_task(test_user.id, TaskCreate(
            title="Research Task",
            agent_type="researcher"
        ))
        
        counts = task_service.count_tasks_by_status(test_user.id, agent_type="finance")
        
        assert counts["pending"] == 1
        
        counts_researcher = task_service.count_tasks_by_status(test_user.id, agent_type="researcher")
        
        assert counts_researcher["pending"] == 1

import pytest
from sqlalchemy import inspect
from app.models.agent_status import AgentStatus, AgentStatusEnum
from app.db.base import Base


def test_agent_status_model_exists():
    """Test that the AgentStatus model is properly defined."""
    assert AgentStatus is not None
    assert hasattr(AgentStatus, '__tablename__')
    assert AgentStatus.__tablename__ == "agent_status"


def test_agent_status_model_inherits_from_base():
    """Test that AgentStatus model inherits from Base."""
    assert issubclass(AgentStatus, Base)


def test_agent_status_model_has_required_columns():
    """Test that AgentStatus model has all required columns."""
    columns = {col.name for col in AgentStatus.__table__.columns}
    required_columns = {
        'id', 'user_id', 'agent_type', 'status', 
        'current_task_id', 'tasks_in_queue', 
        'last_active_at', 'updated_at'
    }
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"


def test_agent_status_id_is_primary_key():
    """Test that id column is the primary key."""
    id_col = AgentStatus.__table__.columns['id']
    assert id_col.primary_key is True
    assert id_col.nullable is False


def test_agent_status_user_id_is_foreign_key():
    """Test that user_id column is a foreign key."""
    user_id_col = AgentStatus.__table__.columns['user_id']
    assert user_id_col.nullable is False
    assert user_id_col.index is True
    
    # Check foreign key constraint
    foreign_keys = list(user_id_col.foreign_keys)
    assert len(foreign_keys) > 0, "user_id should have a foreign key constraint"
    assert foreign_keys[0].column.table.name == "users"


def test_agent_status_current_task_id_is_foreign_key():
    """Test that current_task_id column is a foreign key."""
    current_task_id_col = AgentStatus.__table__.columns['current_task_id']
    assert current_task_id_col.nullable is True
    
    # Check foreign key constraint
    foreign_keys = list(current_task_id_col.foreign_keys)
    assert len(foreign_keys) > 0, "current_task_id should have a foreign key constraint"
    assert foreign_keys[0].column.table.name == "tasks"


def test_agent_status_agent_type_is_not_nullable():
    """Test that agent_type column is not nullable."""
    agent_type_col = AgentStatus.__table__.columns['agent_type']
    assert agent_type_col.nullable is False
    assert agent_type_col.index is True


def test_agent_status_status_is_not_nullable():
    """Test that status column is not nullable."""
    status_col = AgentStatus.__table__.columns['status']
    assert status_col.nullable is False


def test_agent_status_tasks_in_queue_has_default():
    """Test that tasks_in_queue column has a default value."""
    tasks_in_queue_col = AgentStatus.__table__.columns['tasks_in_queue']
    assert tasks_in_queue_col.nullable is False
    assert tasks_in_queue_col.default is not None


def test_agent_status_last_active_at_has_default():
    """Test that last_active_at has a default value."""
    last_active_at_col = AgentStatus.__table__.columns['last_active_at']
    assert last_active_at_col.nullable is False
    assert last_active_at_col.default is not None


def test_agent_status_updated_at_has_default_and_onupdate():
    """Test that updated_at has default and onupdate configured."""
    updated_at_col = AgentStatus.__table__.columns['updated_at']
    assert updated_at_col.nullable is False
    assert updated_at_col.default is not None
    assert updated_at_col.onupdate is not None


def test_agent_status_has_unique_constraint():
    """Test that AgentStatus has a unique constraint on user_id and agent_type."""
    constraints = AgentStatus.__table__.constraints
    unique_constraints = [c for c in constraints if hasattr(c, 'columns') and len(c.columns) == 2]
    
    # Check if there's a unique constraint on user_id and agent_type
    found_constraint = False
    for constraint in unique_constraints:
        column_names = {col.name for col in constraint.columns}
        if column_names == {'user_id', 'agent_type'}:
            found_constraint = True
            break
    
    assert found_constraint, "No unique constraint found on (user_id, agent_type)"


def test_agent_status_enum_values():
    """Test that AgentStatusEnum has the correct values."""
    assert AgentStatusEnum.AVAILABLE.value == "available"
    assert AgentStatusEnum.BUSY.value == "busy"
    assert AgentStatusEnum.IDLE.value == "idle"


def test_agent_status_has_relationship_to_user():
    """Test that AgentStatus has a relationship to User."""
    assert hasattr(AgentStatus, 'user')


def test_agent_status_has_relationship_to_current_task():
    """Test that AgentStatus has a relationship to Task."""
    assert hasattr(AgentStatus, 'current_task')


def test_agent_status_to_dict_method():
    """Test that AgentStatus has a to_dict method."""
    assert hasattr(AgentStatus, 'to_dict')
    assert callable(AgentStatus.to_dict)


def test_agent_status_user_id_index_exists():
    """Test that an index exists on the user_id column."""
    user_id_col = AgentStatus.__table__.columns['user_id']
    assert user_id_col.index is True


def test_agent_status_agent_type_index_exists():
    """Test that an index exists on the agent_type column."""
    agent_type_col = AgentStatus.__table__.columns['agent_type']
    assert agent_type_col.index is True

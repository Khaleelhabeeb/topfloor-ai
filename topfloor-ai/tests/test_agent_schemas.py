"""
Tests for Agent Schemas
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.agent import AgentStatusResponse, AgentStatusEnum


class TestAgentStatusResponse:
    """Tests for AgentStatusResponse schema."""
    
    def test_valid_agent_status_response_minimal(self):
        """Test that valid agent status response data is accepted."""
        status = AgentStatusResponse(
            id=1,
            user_id=1,
            agent_type="finance",
            status=AgentStatusEnum.AVAILABLE,
            current_task_id=None,
            tasks_in_queue=0,
            last_active_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert status.id == 1
        assert status.user_id == 1
        assert status.agent_type == "finance"
        assert status.status == AgentStatusEnum.AVAILABLE
        assert status.current_task_id is None
        assert status.tasks_in_queue == 0
        assert isinstance(status.last_active_at, datetime)
        assert isinstance(status.updated_at, datetime)
    
    def test_valid_agent_status_response_with_task(self):
        """Test agent status response with current task."""
        status = AgentStatusResponse(
            id=1,
            user_id=1,
            agent_type="data_analyst",
            status=AgentStatusEnum.BUSY,
            current_task_id=42,
            tasks_in_queue=3,
            last_active_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert status.status == AgentStatusEnum.BUSY
        assert status.current_task_id == 42
        assert status.tasks_in_queue == 3
    
    def test_agent_status_enum_values(self):
        """Test that all agent status enum values are valid."""
        for status_value in [AgentStatusEnum.AVAILABLE, AgentStatusEnum.BUSY, AgentStatusEnum.IDLE]:
            status = AgentStatusResponse(
                id=1,
                user_id=1,
                agent_type="researcher",
                status=status_value,
                current_task_id=None,
                tasks_in_queue=0,
                last_active_at=datetime.now(),
                updated_at=datetime.now()
            )
            assert status.status == status_value
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError):
            AgentStatusResponse(
                id=1,
                user_id=1,
                agent_type="finance"
            )
    
    def test_invalid_status_value(self):
        """Test that invalid status value is rejected."""
        with pytest.raises(ValidationError):
            AgentStatusResponse(
                id=1,
                user_id=1,
                agent_type="finance",
                status="invalid_status",
                current_task_id=None,
                tasks_in_queue=0,
                last_active_at=datetime.now(),
                updated_at=datetime.now()
            )
    
    def test_from_attributes_config(self):
        """Test that from_attributes is enabled for SQLAlchemy model conversion."""
        assert AgentStatusResponse.model_config.get('from_attributes') is True
    
    def test_agent_status_enum_string_values(self):
        """Test that AgentStatusEnum has correct string values."""
        assert AgentStatusEnum.AVAILABLE.value == "available"
        assert AgentStatusEnum.BUSY.value == "busy"
        assert AgentStatusEnum.IDLE.value == "idle"

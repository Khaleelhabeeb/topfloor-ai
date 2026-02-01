"""
Tests for Agents API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DBSession

from app.main import app
from app.api.dependencies import get_db
from app.models.user import User
from app.core.security import hash_password, create_access_token


@pytest.fixture
def client(db_session: DBSession):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


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
def auth_headers(test_user: User) -> dict:
    """Create authentication headers"""
    token = create_access_token({"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


class TestAgentsAPI:
    """Test suite for Agents API"""
    
    def test_list_agents_unauthorized(self, client: TestClient):
        """Test listing agents without authentication"""
        response = client.get("/agents/")
        assert response.status_code == 401
    
    def test_list_agents_authorized(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test listing agents with authentication"""
        response = client.get("/agents/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        assert "total" in data
        assert isinstance(data["agents"], list)
    
    def test_get_agent_registry(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting agent registry"""
        response = client.get("/agents/registry", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert "agents" in data
        assert data["version"] == "1.0.0"
        assert len(data["agents"]) == 5  # 5 agents in registry
    
    def test_execute_agent_unauthorized(self, client: TestClient):
        """Test executing agent without authentication"""
        response = client.post(
            "/agents/execute",
            json={"message": "Hello"}
        )
        assert response.status_code == 401
    
    def test_execute_agent_with_message(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test executing agent with a message"""
        import pytest
        pytest.skip("Skipping actual agent execution - requires GOOGLE_API_KEY")
        
        response = client.post(
            "/agents/execute",
            headers=auth_headers,
            json={
                "message": "Write a hello world function",
                "agent_type": "developer"
            }
        )
        if response.status_code != 200:
            print(f"Error: {response.json()}")
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "agent_name" in data
        assert "response" in data
        assert data["agent_name"] == "developer"
    
    def test_execute_agent_invalid_type(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test executing agent with invalid type"""
        response = client.post(
            "/agents/execute",
            headers=auth_headers,
            json={
                "message": "Hello",
                "agent_type": "invalid_agent"
            }
        )
        assert response.status_code == 400
        assert "Invalid agent type" in response.json()["detail"]
    
    def test_execute_agent_empty_message(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test executing agent with empty message"""
        response = client.post(
            "/agents/execute",
            headers=auth_headers,
            json={
                "message": ""
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_execute_agent_with_session_resume(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test resuming a session"""
        import pytest
        pytest.skip("Skipping actual agent execution - requires GOOGLE_API_KEY")
        
        # First execution
        response1 = client.post(
            "/agents/execute",
            headers=auth_headers,
            json={"message": "First message"}
        )
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        
        # Resume session
        response2 = client.post(
            "/agents/execute",
            headers=auth_headers,
            json={
                "message": "Second message",
                "session_id": session_id
            }
        )
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
    
    def test_get_session_status(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting session status"""
        import pytest
        pytest.skip("Skipping actual agent execution - requires GOOGLE_API_KEY")
        
        # Create a session first
        response = client.post(
            "/agents/execute",
            headers=auth_headers,
            json={"message": "Test message"}
        )
        session_id = response.json()["session_id"]
        
        # Get status
        status_response = client.get(
            f"/agents/sessions/{session_id}/status",
            headers=auth_headers
        )
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert data["session_id"] == session_id
        assert "status" in data
        assert "agent_type" in data
    
    def test_get_session_status_not_found(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting status of non-existent session"""
        response = client.get(
            "/agents/sessions/sess_nonexistent/status",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestTasksAPI:
    """Test suite for Tasks API"""
    
    def test_create_task_unauthorized(self, client: TestClient):
        """Test creating task without authentication"""
        response = client.post(
            "/tasks/",
            json={
                "title": "Test Task",
                "agent_type": "developer"
            }
        )
        assert response.status_code == 401
    
    def test_create_task(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test creating a task"""
        response = client.post(
            "/tasks/",
            headers=auth_headers,
            json={
                "title": "Write a function",
                "description": "Write a hello world function",
                "agent_type": "developer",
                "priority": "medium"
            }
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Write a function"
        assert data["agent_type"] == "developer"
        assert data["status"] == "pending"
    
    def test_create_task_invalid_agent_type(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test creating task with invalid agent type"""
        response = client.post(
            "/tasks/",
            headers=auth_headers,
            json={
                "title": "Test Task",
                "agent_type": "invalid_agent"
            }
        )
        assert response.status_code == 400
    
    def test_list_tasks(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test listing tasks"""
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    def test_list_tasks_with_filters(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test listing tasks with filters"""
        response = client.get(
            "/tasks/?status=pending&agent_type=developer&page=1&page_size=10",
            headers=auth_headers
        )
        assert response.status_code == 200

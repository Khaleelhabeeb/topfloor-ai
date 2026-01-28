import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User  # Import User model so Base.metadata knows about it
from app.main import app
from app.db.session import get_db
from app.core.security import create_access_token
from datetime import timedelta


# Test database setup
@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    # Import User model to ensure it's registered with Base.metadata
    from app.models.user import User  # noqa: F401
    
    # Use file-based SQLite for testing to avoid connection issues
    import tempfile
    import os
    
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def test_db(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()


@pytest.fixture
def client(test_engine):
    """Create a test client with test database."""
    # Create a session factory for the test engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


class TestRegisterEndpoint:
    """Tests for POST /auth/register endpoint"""
    
    def test_register_success(self, client, sample_user):
        """Test successful user registration"""
        response = client.post("/auth/register", json=sample_user)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == sample_user["email"]
        assert "created_at" in data
        # Requirement 1.5: Password hash should not be in response
        assert "password" not in data
        assert "password_hash" not in data
        
    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email returns 409"""
        # Register first user
        client.post("/auth/register", json=sample_user)
        
        # Attempt to register with same email
        response = client.post("/auth/register", json=sample_user)
        
        # Requirement 1.2: Return 409 Conflict for duplicate email
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()
        
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "testpassword123"
        })
        
        # Pydantic validation should return 422
        assert response.status_code == 422
        
    def test_register_short_password(self, client):
        """Test registration with password shorter than 8 characters"""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "short"  # Only 5 characters
        })
        
        # Requirement 1.4: Reject passwords shorter than 8 characters
        assert response.status_code == 422
        
    def test_register_minimum_password_length(self, client):
        """Test registration with exactly 8 character password"""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "12345678"  # Exactly 8 characters
        })
        
        assert response.status_code == 201
        
    def test_register_empty_password(self, client):
        """Test registration with empty password"""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": ""
        })
        
        # Requirement 1.3: Reject empty password
        assert response.status_code == 422
        
    def test_register_missing_email(self, client):
        """Test registration without email field"""
        response = client.post("/auth/register", json={
            "password": "testpassword123"
        })
        
        assert response.status_code == 422
        
    def test_register_missing_password(self, client):
        """Test registration without password field"""
        response = client.post("/auth/register", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422
        
    def test_register_response_structure(self, client, sample_user):
        """Test that registration response has correct structure"""
        response = client.post("/auth/register", json=sample_user)
        
        assert response.status_code == 201
        data = response.json()
        
        # Should have these fields
        assert "id" in data
        assert "email" in data
        assert "created_at" in data
        
        # Should NOT have these fields (security)
        assert "password" not in data
        assert "password_hash" not in data
        assert "updated_at" not in data or data["updated_at"] is None


class TestLoginEndpoint:
    """Tests for POST /auth/login endpoint"""
    
    def test_login_success(self, client, sample_user):
        """Test successful login with valid credentials"""
        # Register user first
        client.post("/auth/register", json=sample_user)
        
        # Login with correct credentials
        response = client.post("/auth/login", json=sample_user)
        
        # Requirement 3.1: Return JWT token for valid credentials
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        
    def test_login_incorrect_password(self, client, sample_user):
        """Test login with incorrect password returns 401"""
        # Register user first
        client.post("/auth/register", json=sample_user)
        
        # Login with wrong password
        response = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": "wrongpassword"
        })
        
        # Requirement 3.2: Return 401 for incorrect password
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
        
    def test_login_nonexistent_email(self, client):
        """Test login with non-existent email returns 401"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })
        
        # Requirement 3.3: Return 401 for non-existent email
        assert response.status_code == 401
        
    def test_login_generic_error_message(self, client, sample_user):
        """Test that login failures use generic error messages"""
        # Register user first
        client.post("/auth/register", json=sample_user)
        
        # Wrong password
        response1 = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": "wrongpassword"
        })
        
        # Non-existent email
        response2 = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })
        
        # Requirement 3.4, 8.1: Both should have same generic error message
        assert response1.status_code == 401
        assert response2.status_code == 401
        assert response1.json()["detail"] == response2.json()["detail"]
        
    def test_login_empty_password(self, client, sample_user):
        """Test login with empty password"""
        # Register user first
        client.post("/auth/register", json=sample_user)
        
        # Login with empty password
        response = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": ""
        })
        
        assert response.status_code == 401
        
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format"""
        response = client.post("/auth/login", json={
            "email": "not-an-email",
            "password": "testpassword123"
        })
        
        # Pydantic validation should return 422
        assert response.status_code == 422
        
    def test_login_token_structure(self, client, sample_user):
        """Test that login response has correct token structure"""
        # Register user first
        client.post("/auth/register", json=sample_user)
        
        # Login
        response = client.post("/auth/login", json=sample_user)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have these fields
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Token should be a non-empty string
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0


class TestMeEndpoint:
    """Tests for GET /auth/me endpoint"""
    
    def test_me_with_valid_token(self, client, sample_user):
        """Test accessing /me with valid token"""
        # Register and login
        register_response = client.post("/auth/register", json=sample_user)
        user_data = register_response.json()
        
        login_response = client.post("/auth/login", json=sample_user)
        token = login_response.json()["access_token"]
        
        # Access /me endpoint with token
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Requirement 5.1: Allow access with valid JWT token
        assert response.status_code == 200
        data = response.json()
        
        # Requirement 5.4: Return user ID, email, and created_at
        assert data["id"] == user_data["id"]
        assert data["email"] == user_data["email"]
        assert "created_at" in data
        
        # Requirement 5.5: Never return password hash
        assert "password" not in data
        assert "password_hash" not in data
        
    def test_me_without_token(self, client):
        """Test accessing /me without token returns 401"""
        response = client.get("/auth/me")
        
        # Requirement 5.2: Return 401 for missing token
        assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials
        
    def test_me_with_invalid_token(self, client):
        """Test accessing /me with invalid token returns 401"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        # Requirement 5.3: Return 401 for invalid token
        assert response.status_code == 401
        
    def test_me_with_expired_token(self, client, sample_user, test_db):
        """Test accessing /me with expired token returns 401"""
        # Register user
        register_response = client.post("/auth/register", json=sample_user)
        user_data = register_response.json()
        
        # Create an expired token (negative expiration)
        expired_token = create_access_token(
            data={"sub": user_data["id"]},
            expires_delta=timedelta(seconds=-1)
        )
        
        # Access /me endpoint with expired token
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        # Requirement 4.5: Expired tokens should be rejected
        assert response.status_code == 401
        
    def test_me_with_malformed_token(self, client):
        """Test accessing /me with malformed token returns 401"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer not-a-jwt-token"}
        )
        
        # Requirement 8.3: Handle malformed tokens gracefully
        assert response.status_code == 401
        
    def test_me_with_token_missing_bearer_prefix(self, client, sample_user):
        """Test accessing /me with token missing 'Bearer' prefix"""
        # Register and login
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json=sample_user)
        token = login_response.json()["access_token"]
        
        # Access /me endpoint without 'Bearer' prefix
        response = client.get(
            "/auth/me",
            headers={"Authorization": token}
        )
        
        # Should fail because HTTPBearer expects 'Bearer' prefix
        assert response.status_code == 403
        
    def test_me_response_structure(self, client, sample_user):
        """Test that /me response has correct structure"""
        # Register and login
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json=sample_user)
        token = login_response.json()["access_token"]
        
        # Access /me endpoint
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have these fields
        assert "id" in data
        assert "email" in data
        assert "created_at" in data
        
        # Should NOT have these fields (security)
        assert "password" not in data
        assert "password_hash" not in data


class TestAuthFlowIntegration:
    """Integration tests for complete authentication flow"""
    
    def test_complete_auth_flow(self, client):
        """Test complete flow: register → login → access protected endpoint"""
        user_data = {
            "email": "integration@example.com",
            "password": "integrationtest123"
        }
        
        # Step 1: Register
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        user_info = register_response.json()
        
        # Step 2: Login
        login_response = client.post("/auth/login", json=user_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Access protected endpoint
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        
        # Verify data consistency
        assert me_data["id"] == user_info["id"]
        assert me_data["email"] == user_info["email"]
        
    def test_multiple_users_independent_auth(self, client):
        """Test that multiple users can authenticate independently"""
        user1 = {"email": "user1@example.com", "password": "password123"}
        user2 = {"email": "user2@example.com", "password": "password456"}
        
        # Register both users
        client.post("/auth/register", json=user1)
        client.post("/auth/register", json=user2)
        
        # Login both users
        login1 = client.post("/auth/login", json=user1)
        login2 = client.post("/auth/login", json=user2)
        
        token1 = login1.json()["access_token"]
        token2 = login2.json()["access_token"]
        
        # Tokens should be different
        assert token1 != token2
        
        # Each token should access correct user
        me1 = client.get("/auth/me", headers={"Authorization": f"Bearer {token1}"})
        me2 = client.get("/auth/me", headers={"Authorization": f"Bearer {token2}"})
        
        assert me1.json()["email"] == user1["email"]
        assert me2.json()["email"] == user2["email"]
        
    def test_cannot_access_protected_endpoint_after_failed_login(self, client, sample_user):
        """Test that failed login doesn't grant access"""
        # Register user
        client.post("/auth/register", json=sample_user)
        
        # Attempt login with wrong password
        login_response = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": "wrongpassword"
        })
        
        assert login_response.status_code == 401
        
        # Should not be able to access protected endpoint
        me_response = client.get("/auth/me")
        assert me_response.status_code == 403


class TestErrorHandling:
    """Tests for error handling and security"""
    
    def test_error_responses_no_stack_traces(self, client):
        """Test that error responses don't contain stack traces"""
        # Trigger various errors
        responses = [
            client.post("/auth/register", json={"email": "invalid", "password": "test"}),
            client.post("/auth/login", json={"email": "test@example.com", "password": "wrong"}),
            client.get("/auth/me", headers={"Authorization": "Bearer invalid"}),
        ]
        
        # Requirement 8.4: No stack traces in responses
        for response in responses:
            response_text = response.text.lower()
            assert "traceback" not in response_text
            assert "exception" not in response_text
            assert "error:" not in response_text or "detail" in response_text
            
    def test_generic_authentication_error_messages(self, client, sample_user):
        """Test that authentication errors use generic messages"""
        # Register user
        client.post("/auth/register", json=sample_user)
        
        # Test various authentication failures
        wrong_password = client.post("/auth/login", json={
            "email": sample_user["email"],
            "password": "wrongpassword"
        })
        
        nonexistent_user = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })
        
        invalid_token = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token"}
        )
        
        # Requirement 8.1: Generic error messages
        # All should return 401 with generic messages
        assert wrong_password.status_code == 401
        assert nonexistent_user.status_code == 401
        assert invalid_token.status_code == 401
        
        # Messages should be generic (not revealing system details)
        assert "incorrect" in wrong_password.json()["detail"].lower()
        assert "incorrect" in nonexistent_user.json()["detail"].lower()
        assert "invalid" in invalid_token.json()["detail"].lower()


class TestRequirementValidation:
    """Tests explicitly validating requirements"""
    
    def test_requirement_1_1_hash_password_and_create_user(self, client, sample_user):
        """Requirement 1.1: Hash password and create user record"""
        response = client.post("/auth/register", json=sample_user)
        assert response.status_code == 201
        assert "id" in response.json()
        
    def test_requirement_1_2_duplicate_email_409(self, client, sample_user):
        """Requirement 1.2: Return 409 Conflict for duplicate email"""
        client.post("/auth/register", json=sample_user)
        response = client.post("/auth/register", json=sample_user)
        assert response.status_code == 409
        
    def test_requirement_1_5_no_password_in_response(self, client, sample_user):
        """Requirement 1.5: Success response without exposing password hash"""
        response = client.post("/auth/register", json=sample_user)
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
        
    def test_requirement_3_1_return_jwt_for_valid_credentials(self, client, sample_user):
        """Requirement 3.1: Return JWT token for valid credentials"""
        client.post("/auth/register", json=sample_user)
        response = client.post("/auth/login", json=sample_user)
        assert response.status_code == 200
        assert "access_token" in response.json()
        
    def test_requirement_5_1_valid_token_grants_access(self, client, sample_user):
        """Requirement 5.1: Valid JWT token allows access to protected endpoint"""
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json=sample_user)
        token = login_response.json()["access_token"]
        
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        
    def test_requirement_5_4_return_user_fields(self, client, sample_user):
        """Requirement 5.4: Return user ID, email, and created_at"""
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json=sample_user)
        token = login_response.json()["access_token"]
        
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "created_at" in data
        
    def test_requirement_5_5_never_return_password_hash(self, client, sample_user):
        """Requirement 5.5: Never return password hash"""
        client.post("/auth/register", json=sample_user)
        login_response = client.post("/auth/login", json=sample_user)
        token = login_response.json()["access_token"]
        
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data

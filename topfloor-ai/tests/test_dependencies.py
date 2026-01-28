import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.db.base import Base
from app.api.dependencies import get_current_user
from app.core.security import create_access_token
from app.schemas.user import UserCreate
from app.services.user_service import UserService


# Test database setup
@pytest.fixture(scope="function")
def db_session():
    """Create a test database for each test function."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestGetCurrentUser:
    """Tests for get_current_user dependency"""
    
    def test_get_current_user_with_valid_token(self, db_session):
        """Test that valid token returns user object"""
        # Create a test user
        user_service = UserService(db_session)
        user_data = UserCreate(email="test@example.com", password="password123")
        created_user = user_service.create_user(user_data)
        
        # Create valid token for this user
        token = create_access_token({"sub": created_user.id})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Call dependency
        user = get_current_user(credentials, db_session)
        
        # Verify user is returned
        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email
        
    def test_get_current_user_with_invalid_token(self, db_session):
        """Test that invalid token raises 401"""
        # Create invalid token
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )
        
        # Should raise HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in exc_info.value.detail
        
    def test_get_current_user_with_malformed_token(self, db_session):
        """Test that malformed token raises 401"""
        # Create malformed token
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="not-a-jwt"
        )
        
        # Should raise HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        
    def test_get_current_user_with_nonexistent_user_id(self, db_session):
        """Test that token with non-existent user ID raises 401"""
        # Create token with user ID that doesn't exist
        token = create_access_token({"sub": 99999})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Should raise HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail
        
    def test_get_current_user_with_missing_sub_claim(self, db_session):
        """Test that token without 'sub' claim raises 401"""
        # Create token without 'sub' claim
        token = create_access_token({"user": 123})  # Wrong claim name
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Should raise HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        
    def test_get_current_user_with_string_user_id(self, db_session):
        """Test that token with string user ID is converted to int"""
        # Create a test user
        user_service = UserService(db_session)
        user_data = UserCreate(email="test2@example.com", password="password123")
        created_user = user_service.create_user(user_data)
        
        # Create token with string user ID (JWT stores as string)
        token = create_access_token({"sub": str(created_user.id)})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Call dependency
        user = get_current_user(credentials, db_session)
        
        # Verify user is returned
        assert user is not None
        assert user.id == created_user.id
        
    def test_get_current_user_with_invalid_user_id_format(self, db_session):
        """Test that token with non-numeric user ID raises 401"""
        # Create token with invalid user ID format
        token = create_access_token({"sub": "not-a-number"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Should raise HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401


class TestDependencyRequirements:
    """Tests validating specific requirements"""
    
    def test_requirement_7_1_extracts_token_from_header(self, db_session):
        """Requirement 7.1: Extract JWT token from Authorization header"""
        # Create user and token
        user_service = UserService(db_session)
        user_data = UserCreate(email="test3@example.com", password="password123")
        created_user = user_service.create_user(user_data)
        token = create_access_token({"sub": created_user.id})
        
        # HTTPBearer extracts token, we verify it's used correctly
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = get_current_user(credentials, db_session)
        
        assert user is not None
        
    def test_requirement_7_2_loads_user_from_database(self, db_session):
        """Requirement 7.2: Load user from database for valid token"""
        # Create user
        user_service = UserService(db_session)
        user_data = UserCreate(email="test4@example.com", password="password123")
        created_user = user_service.create_user(user_data)
        
        # Create token and get user
        token = create_access_token({"sub": created_user.id})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = get_current_user(credentials, db_session)
        
        # Verify user was loaded from database
        assert user.id == created_user.id
        assert user.email == created_user.email
        assert user.password_hash == created_user.password_hash
        
    def test_requirement_7_3_raises_401_for_invalid_token(self, db_session):
        """Requirement 7.3: Raise 401 for invalid or missing token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        
    def test_requirement_7_4_raises_401_for_nonexistent_user(self, db_session):
        """Requirement 7.4: Raise 401 for non-existent user IDs"""
        token = create_access_token({"sub": 99999})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail

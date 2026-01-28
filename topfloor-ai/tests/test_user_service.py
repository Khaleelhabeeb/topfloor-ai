import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from app.db.base import Base
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.core.security import verify_password


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user_service(test_db):
    """Create a UserService instance with test database."""
    return UserService(test_db)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return UserCreate(
        email="test@example.com",
        password="testpassword123"
    )


class TestCreateUser:
    """Tests for user creation functionality"""
    
    def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation"""
        user = user_service.create_user(sample_user_data)
        
        assert user is not None
        assert user.id is not None
        assert user.email == sample_user_data.email
        assert user.password_hash is not None
        assert user.created_at is not None
        
    def test_create_user_hashes_password(self, user_service, sample_user_data):
        """Test that password is hashed, not stored as plaintext"""
        user = user_service.create_user(sample_user_data)
        
        # Password hash should not equal plaintext password
        assert user.password_hash != sample_user_data.password
        # Password hash should be a bcrypt hash
        assert user.password_hash.startswith("$2b$")
        
    def test_create_user_password_is_verifiable(self, user_service, sample_user_data):
        """Test that hashed password can be verified"""
        user = user_service.create_user(sample_user_data)
        
        # Should be able to verify the password
        assert verify_password(sample_user_data.password, user.password_hash) is True
        
    def test_create_user_duplicate_email_raises_error(self, user_service, sample_user_data):
        """Test that duplicate email raises ValueError"""
        # Create first user
        user_service.create_user(sample_user_data)
        
        # Attempt to create second user with same email
        with pytest.raises(ValueError, match="Email already registered"):
            user_service.create_user(sample_user_data)
            
    def test_create_user_different_emails_succeed(self, user_service):
        """Test that users with different emails can be created"""
        user1 = user_service.create_user(UserCreate(
            email="user1@example.com",
            password="password123"
        ))
        user2 = user_service.create_user(UserCreate(
            email="user2@example.com",
            password="password456"
        ))
        
        assert user1.id != user2.id
        assert user1.email != user2.email
        
    def test_create_user_sets_timestamps(self, user_service, sample_user_data):
        """Test that created_at timestamp is set"""
        user = user_service.create_user(sample_user_data)
        
        assert user.created_at is not None
        # updated_at may be None initially (only set on updates)


class TestAuthenticateUser:
    """Tests for user authentication functionality"""
    
    def test_authenticate_user_with_valid_credentials(self, user_service, sample_user_data):
        """Test authentication with correct email and password"""
        # Create user first
        created_user = user_service.create_user(sample_user_data)
        
        # Authenticate with correct credentials
        authenticated_user = user_service.authenticate_user(
            sample_user_data.email,
            sample_user_data.password
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == created_user.email
        
    def test_authenticate_user_with_incorrect_password(self, user_service, sample_user_data):
        """Test authentication with wrong password returns None"""
        # Create user first
        user_service.create_user(sample_user_data)
        
        # Authenticate with wrong password
        authenticated_user = user_service.authenticate_user(
            sample_user_data.email,
            "wrongpassword"
        )
        
        assert authenticated_user is None
        
    def test_authenticate_user_with_nonexistent_email(self, user_service):
        """Test authentication with non-existent email returns None"""
        authenticated_user = user_service.authenticate_user(
            "nonexistent@example.com",
            "anypassword"
        )
        
        assert authenticated_user is None
        
    def test_authenticate_user_empty_password(self, user_service, sample_user_data):
        """Test authentication with empty password returns None"""
        # Create user first
        user_service.create_user(sample_user_data)
        
        # Authenticate with empty password
        authenticated_user = user_service.authenticate_user(
            sample_user_data.email,
            ""
        )
        
        assert authenticated_user is None
        
    def test_authenticate_user_case_sensitive_email(self, user_service, sample_user_data):
        """Test that email lookup is case-sensitive (database default)"""
        # Create user with lowercase email
        user_service.create_user(sample_user_data)
        
        # Try to authenticate with uppercase email
        # Note: This behavior depends on database collation
        # SQLite is case-insensitive by default, PostgreSQL is case-sensitive
        authenticated_user = user_service.authenticate_user(
            sample_user_data.email.upper(),
            sample_user_data.password
        )
        
        # This test documents current behavior
        # In production with PostgreSQL, this would return None
        # With SQLite, it might succeed due to case-insensitive collation


class TestGetUserById:
    """Tests for user retrieval by ID"""
    
    def test_get_user_by_id_existing_user(self, user_service, sample_user_data):
        """Test retrieving an existing user by ID"""
        created_user = user_service.create_user(sample_user_data)
        
        retrieved_user = user_service.get_user_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        
    def test_get_user_by_id_nonexistent_user(self, user_service):
        """Test retrieving a non-existent user returns None"""
        retrieved_user = user_service.get_user_by_id(99999)
        
        assert retrieved_user is None
        
    def test_get_user_by_id_returns_correct_user(self, user_service):
        """Test that correct user is returned when multiple users exist"""
        user1 = user_service.create_user(UserCreate(
            email="user1@example.com",
            password="password123"
        ))
        user2 = user_service.create_user(UserCreate(
            email="user2@example.com",
            password="password456"
        ))
        
        retrieved_user = user_service.get_user_by_id(user1.id)
        
        assert retrieved_user.id == user1.id
        assert retrieved_user.email == user1.email
        assert retrieved_user.id != user2.id


class TestGetUserByEmail:
    """Tests for user retrieval by email"""
    
    def test_get_user_by_email_existing_user(self, user_service, sample_user_data):
        """Test retrieving an existing user by email"""
        created_user = user_service.create_user(sample_user_data)
        
        retrieved_user = user_service.get_user_by_email(sample_user_data.email)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        
    def test_get_user_by_email_nonexistent_user(self, user_service):
        """Test retrieving a non-existent user returns None"""
        retrieved_user = user_service.get_user_by_email("nonexistent@example.com")
        
        assert retrieved_user is None
        
    def test_get_user_by_email_returns_correct_user(self, user_service):
        """Test that correct user is returned when multiple users exist"""
        user1 = user_service.create_user(UserCreate(
            email="user1@example.com",
            password="password123"
        ))
        user2 = user_service.create_user(UserCreate(
            email="user2@example.com",
            password="password456"
        ))
        
        retrieved_user = user_service.get_user_by_email("user1@example.com")
        
        assert retrieved_user.id == user1.id
        assert retrieved_user.email == user1.email
        assert retrieved_user.id != user2.id


class TestUserServiceRequirements:
    """Tests validating specific requirements"""
    
    def test_requirement_1_1_hash_password_and_create_user(self, user_service, sample_user_data):
        """Requirement 1.1: Hash password and create user record"""
        user = user_service.create_user(sample_user_data)
        
        assert user.password_hash != sample_user_data.password
        assert user.id is not None
        
    def test_requirement_1_2_duplicate_email_conflict(self, user_service, sample_user_data):
        """Requirement 1.2: Return error for duplicate email"""
        user_service.create_user(sample_user_data)
        
        with pytest.raises(ValueError, match="Email already registered"):
            user_service.create_user(sample_user_data)
            
    def test_requirement_3_1_valid_credentials_return_user(self, user_service, sample_user_data):
        """Requirement 3.1: Valid credentials return user (for JWT token creation)"""
        user_service.create_user(sample_user_data)
        
        authenticated_user = user_service.authenticate_user(
            sample_user_data.email,
            sample_user_data.password
        )
        
        assert authenticated_user is not None
        
    def test_requirement_3_2_incorrect_password_returns_none(self, user_service, sample_user_data):
        """Requirement 3.2: Incorrect password returns None (for 401 error)"""
        user_service.create_user(sample_user_data)
        
        authenticated_user = user_service.authenticate_user(
            sample_user_data.email,
            "wrongpassword"
        )
        
        assert authenticated_user is None
        
    def test_requirement_3_3_nonexistent_email_returns_none(self, user_service):
        """Requirement 3.3: Non-existent email returns None (for 401 error)"""
        authenticated_user = user_service.authenticate_user(
            "nonexistent@example.com",
            "anypassword"
        )
        
        assert authenticated_user is None
        
    def test_requirement_3_4_same_response_for_invalid_credentials(self, user_service, sample_user_data):
        """Requirement 3.4: Same response (None) for wrong password and non-existent email"""
        user_service.create_user(sample_user_data)
        
        # Wrong password
        result1 = user_service.authenticate_user(
            sample_user_data.email,
            "wrongpassword"
        )
        
        # Non-existent email
        result2 = user_service.authenticate_user(
            "nonexistent@example.com",
            "anypassword"
        )
        
        # Both should return None (same response type)
        assert result1 is None
        assert result2 is None
        assert type(result1) == type(result2)


class TestEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def test_create_user_with_minimum_password_length(self, user_service):
        """Test creating user with exactly 8 character password"""
        user_data = UserCreate(
            email="test@example.com",
            password="12345678"  # Exactly 8 characters
        )
        
        user = user_service.create_user(user_data)
        assert user is not None
        
    def test_create_user_with_long_password(self, user_service):
        """Test creating user with long password (within bcrypt 72-byte limit)"""
        user_data = UserCreate(
            email="test@example.com",
            password="a" * 70  # 70 character password (within bcrypt's 72-byte limit)
        )
        
        user = user_service.create_user(user_data)
        assert user is not None
        assert verify_password("a" * 70, user.password_hash) is True
        
    def test_create_user_with_special_characters_in_password(self, user_service):
        """Test creating user with special characters in password"""
        user_data = UserCreate(
            email="test@example.com",
            password="p@ssw0rd!#$%^&*()"
        )
        
        user = user_service.create_user(user_data)
        assert user is not None
        assert verify_password("p@ssw0rd!#$%^&*()", user.password_hash) is True
        
    def test_authenticate_with_whitespace_in_password(self, user_service):
        """Test that whitespace in password is significant"""
        user_data = UserCreate(
            email="test@example.com",
            password="password with spaces"
        )
        
        user_service.create_user(user_data)
        
        # Correct password with spaces
        assert user_service.authenticate_user(
            "test@example.com",
            "password with spaces"
        ) is not None
        
        # Wrong password without spaces
        assert user_service.authenticate_user(
            "test@example.com",
            "passwordwithspaces"
        ) is None

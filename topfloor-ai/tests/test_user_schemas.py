import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token


class TestUserCreate:
    """Tests for UserCreate schema."""
    
    def test_valid_user_create(self):
        """Test that valid email and password are accepted."""
        user = UserCreate(email="test@example.com", password="Password123!")
        assert user.email == "test@example.com"
        assert user.password == "Password123!"
    
    def test_invalid_email_format(self):
        """Test that invalid email format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="not-an-email", password="Password123!")
        
        errors = exc_info.value.errors()
        assert any(error['type'] == 'value_error' for error in errors)
    
    def test_password_too_short(self):
        """Test that password shorter than 8 characters is rejected.
        
        Requirements: 1.4
        """
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="short")
        
        errors = exc_info.value.errors()
        assert any('min_length' in str(error) for error in errors)
    
    def test_password_exactly_8_characters(self):
        """Test that password with exactly 8 characters is rejected if it doesn't meet complexity requirements."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="12345678")
        assert "Password must contain at least one uppercase letter" in str(exc_info.value)
    
    def test_missing_email(self):
        """Test that missing email is rejected."""
        with pytest.raises(ValidationError):
            UserCreate(password="password123")
    
    def test_missing_password(self):
        """Test that missing password is rejected."""
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com")
    
    def test_empty_password(self):
        """Test that empty password is rejected.
        
        Requirements: 1.3
        """
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="")


class TestUserLogin:
    """Tests for UserLogin schema."""
    
    def test_valid_user_login(self):
        """Test that valid login credentials are accepted."""
        login = UserLogin(email="test@example.com", password="anypassword")
        assert login.email == "test@example.com"
        assert login.password == "anypassword"
    
    def test_invalid_email_format(self):
        """Test that invalid email format is rejected."""
        with pytest.raises(ValidationError):
            UserLogin(email="not-an-email", password="password")
    
    def test_no_password_length_validation(self):
        """Test that UserLogin accepts any password length (checking existing credentials)."""
        # This should work even with short password since we're validating existing credentials
        login = UserLogin(email="test@example.com", password="short")
        assert login.password == "short"


class TestUserResponse:
    """Tests for UserResponse schema."""
    
    def test_valid_user_response(self):
        """Test that valid user response data is accepted."""
        user = UserResponse(
            id=1,
            email="test@example.com",
            created_at=datetime.now()
        )
        assert user.id == 1
        assert user.email == "test@example.com"
        assert isinstance(user.created_at, datetime)
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError):
            UserResponse(id=1, email="test@example.com")
    
    def test_from_attributes_config(self):
        """Test that from_attributes is enabled for SQLAlchemy model conversion."""
        assert UserResponse.model_config.get('from_attributes') is True


class TestToken:
    """Tests for Token schema."""
    
    def test_valid_token(self):
        """Test that valid token data is accepted."""
        token = Token(access_token="some.jwt.token")
        assert token.access_token == "some.jwt.token"
        assert token.token_type == "bearer"
    
    def test_custom_token_type(self):
        """Test that token_type can be customized."""
        token = Token(access_token="some.jwt.token", token_type="custom")
        assert token.token_type == "custom"
    
    def test_default_token_type(self):
        """Test that token_type defaults to 'bearer'."""
        token = Token(access_token="some.jwt.token")
        assert token.token_type == "bearer"
    
    def test_missing_access_token(self):
        """Test that missing access_token is rejected."""
        with pytest.raises(ValidationError):
            Token()

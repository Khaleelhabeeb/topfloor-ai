import pytest
from datetime import timedelta
import time
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """Tests for password hashing functionality"""
    
    def test_hash_password_returns_different_from_plaintext(self):
        """Password hash should be different from plaintext"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed != password
        
    def test_hash_password_produces_bcrypt_hash(self):
        """Hash should be a bcrypt hash (starts with $2b$)"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed.startswith("$2b$")
        
    def test_same_password_produces_different_hashes(self):
        """Same password should produce different hashes (unique salt)"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        
    def test_verify_password_with_correct_password(self):
        """Correct password should verify successfully"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        
    def test_verify_password_with_incorrect_password(self):
        """Incorrect password should fail verification"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False
        
    def test_verify_password_with_empty_password(self):
        """Empty password should fail verification"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Tests for JWT token creation and validation"""
    
    def test_create_access_token_returns_string(self):
        """Token creation should return a string"""
        token = create_access_token({"sub": 123})
        assert isinstance(token, str)
        assert len(token) > 0
        
    def test_create_access_token_with_integer_user_id(self):
        """Token should handle integer user IDs"""
        token = create_access_token({"sub": 123})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "123"  # Converted to string
        
    def test_create_access_token_with_string_user_id(self):
        """Token should handle string user IDs"""
        token = create_access_token({"sub": "456"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "456"
        
    def test_decode_access_token_returns_payload(self):
        """Valid token should decode to payload"""
        user_id = 123
        token = create_access_token({"sub": user_id})
        payload = decode_access_token(token)
        assert payload is not None
        assert "sub" in payload
        assert "exp" in payload
        
    def test_decode_access_token_contains_user_id(self):
        """Decoded token should contain user ID"""
        user_id = 789
        token = create_access_token({"sub": user_id})
        payload = decode_access_token(token)
        assert payload.get("sub") == str(user_id)
        
    def test_decode_access_token_contains_expiration(self):
        """Decoded token should contain expiration"""
        token = create_access_token({"sub": 123})
        payload = decode_access_token(token)
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
        
    def test_decode_access_token_with_invalid_token(self):
        """Invalid token should return None"""
        invalid_token = "invalid.token.here"
        payload = decode_access_token(invalid_token)
        assert payload is None
        
    def test_decode_access_token_with_malformed_token(self):
        """Malformed token should return None"""
        malformed_token = "not-a-jwt-token"
        payload = decode_access_token(malformed_token)
        assert payload is None
        
    def test_decode_access_token_with_expired_token(self):
        """Expired token should return None"""
        # Create token that expires immediately
        token = create_access_token(
            {"sub": 123},
            expires_delta=timedelta(seconds=-1)
        )
        # Wait a bit to ensure expiration
        time.sleep(0.1)
        payload = decode_access_token(token)
        assert payload is None
        
    def test_create_access_token_with_custom_expiration(self):
        """Token should respect custom expiration"""
        token = create_access_token(
            {"sub": 123},
            expires_delta=timedelta(minutes=60)
        )
        payload = decode_access_token(token)
        assert payload is not None
        # Verify expiration is set (we can't check exact value due to timing)
        assert "exp" in payload


class TestSecurityRequirements:
    """Tests validating specific security requirements"""
    
    def test_requirement_2_1_uses_bcrypt(self):
        """Requirement 2.1: Uses bcrypt for password hashing"""
        hashed = hash_password("test")
        # Bcrypt hashes start with $2b$ (or $2a$, $2y$)
        assert hashed.startswith("$2")
        
    def test_requirement_2_4_unique_salt(self):
        """Requirement 2.4: Generates unique salt for each password"""
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        
    def test_requirement_4_2_jwt_includes_user_id(self):
        """Requirement 4.2: JWT includes user ID claim"""
        token = create_access_token({"sub": 456})
        payload = decode_access_token(token)
        assert "sub" in payload
        assert payload["sub"] == "456"
        
    def test_requirement_4_3_jwt_includes_expiration(self):
        """Requirement 4.3: JWT includes expiration claim"""
        token = create_access_token({"sub": 123})
        payload = decode_access_token(token)
        assert "exp" in payload
        
    def test_requirement_4_5_expired_tokens_rejected(self):
        """Requirement 4.5: Expired tokens are rejected"""
        expired_token = create_access_token(
            {"sub": 789},
            expires_delta=timedelta(seconds=-1)
        )
        time.sleep(0.1)
        assert decode_access_token(expired_token) is None

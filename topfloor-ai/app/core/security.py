"""
Security Module

This module provides core security functions for password hashing and JWT token management.
It uses bcrypt for password hashing and python-jose for JWT operations.

Functions:
- hash_password(): Hash a password using bcrypt
- verify_password(): Verify a password against its hash with constant-time comparison
- create_access_token(): Create a JWT access token with user ID and expiration
- decode_access_token(): Decode and validate a JWT token with error handling
"""

import os
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

# JWT configuration - load from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-use-strong-random-value-at-least-32-characters")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Each call generates a unique salt, so the same password will produce
    different hashes on subsequent calls.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        The hashed password as a string
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> hashed != "mypassword123"
        True
    """
    # Convert password to bytes and generate salt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using constant-time comparison.
    
    This function uses bcrypt's built-in constant-time comparison to prevent
    timing attacks that could reveal information about the password.
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if the password matches the hash, False otherwise
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    # Convert both to bytes for bcrypt
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with user ID and expiration.
    
    The token is signed with the SECRET_KEY and includes an expiration claim.
    By default, tokens expire after ACCESS_TOKEN_EXPIRE_MINUTES.
    
    Args:
        data: Dictionary containing claims to encode (typically {"sub": user_id})
        expires_delta: Optional custom expiration timedelta. If None, uses default.
        
    Returns:
        The encoded JWT token as a string
        
    Example:
        >>> token = create_access_token({"sub": 123})
        >>> isinstance(token, str)
        True
        >>> len(token) > 0
        True
    """
    to_encode = data.copy()
    
    # Ensure 'sub' claim is a string (JWT spec requirement)
    if 'sub' in to_encode and not isinstance(to_encode['sub'], str):
        to_encode['sub'] = str(to_encode['sub'])
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token with error handling.
    
    This function verifies the token signature and checks expiration.
    Returns None for any JWT error (expired, invalid signature, malformed).
    
    Args:
        token: The JWT token string to decode
        
    Returns:
        Dictionary containing the token payload if valid, None otherwise
        
    Example:
        >>> token = create_access_token({"sub": 123})
        >>> payload = decode_access_token(token)
        >>> payload is not None
        True
        >>> payload.get("sub")
        123
        >>> decode_access_token("invalid.token.here")
        None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

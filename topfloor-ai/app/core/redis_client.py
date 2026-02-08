"""
Redis Client Configuration
Provides a configured Redis client for direct Redis operations
"""

import redis
from redis.connection import SSLConnection
from typing import Optional
from app.core.config import settings


class RedisClient:
    """
    Redis client wrapper with connection pooling.
    """
    
    _instance: Optional[redis.Redis] = None
    _pool: Optional[redis.ConnectionPool] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        Get or create a Redis client instance.
        Uses connection pooling for better performance.
        
        Returns:
            Configured Redis client
        """
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance
    
    @classmethod
    def _create_client(cls) -> redis.Redis:
        """
        Create a new Redis client with proper configuration.
        
        Returns:
            Configured Redis client
        """
        # If SSL is enabled, use from_url with rediss:// protocol
        if settings.REDIS_SSL:
            redis_url = settings.redis_url
            return redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=50,
                ssl_cert_reqs=None  # Don't verify SSL cert
            )
        
        # Otherwise use connection pool
        pool_kwargs = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DB,
            "decode_responses": True,
            "username": settings.REDIS_USERNAME,
            "max_connections": 50,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
        }
        
        # Add password if provided
        if settings.REDIS_PASSWORD:
            pool_kwargs["password"] = settings.REDIS_PASSWORD
        
        # Create connection pool
        cls._pool = redis.ConnectionPool(**pool_kwargs)
        
        # Create Redis client
        return redis.Redis(connection_pool=cls._pool)
    
    @classmethod
    def close(cls):
        """Close the Redis connection pool."""
        if cls._pool:
            cls._pool.disconnect()
            cls._pool = None
            cls._instance = None
    
    @classmethod
    def ping(cls) -> bool:
        """
        Test Redis connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            client = cls.get_client()
            return client.ping()
        except Exception:
            return False
    
    @classmethod
    def get_info(cls) -> dict:
        """
        Get Redis server information.
        
        Returns:
            Dictionary with Redis server info
        """
        try:
            client = cls.get_client()
            return client.info()
        except Exception as e:
            return {"error": str(e)}


# Global Redis client instance
def get_redis_client() -> redis.Redis:
    """
    Get the global Redis client instance.
    
    Returns:
        Configured Redis client
    """
    return RedisClient.get_client()


# Test connection on import (optional)
def test_redis_connection():
    """Test Redis connection and print status."""
    try:
        client = get_redis_client()
        if client.ping():
            print("✓ Redis connection successful")
            info = client.info("server")
            print(f"  Redis version: {info.get('redis_version', 'unknown')}")
            print(f"  Connected to: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            return True
        else:
            print("✗ Redis connection failed: ping returned False")
            return False
    except Exception as e:
        print(f"✗ Redis connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Test connection when run directly
    test_redis_connection()

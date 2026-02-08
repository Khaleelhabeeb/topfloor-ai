"""
Configuration settings for TopFloor AI Platform
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./topfloor_dev.db")
    
    # Memory System - Chroma Cloud
    CHROMA_API_KEY: Optional[str] = os.getenv("CHROMA_API_KEY")
    CHROMA_TENANT: str = os.getenv("CHROMA_TENANT", "733bcc53-ea72-4613-81b9-9f7baa2331a3")
    CHROMA_DATABASE: str = os.getenv("CHROMA_DATABASE", "topfloor")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    MEMORY_ENABLED: bool = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
    
    # Memory Pruning Settings
    MEMORY_PRUNE_DAYS: int = int(os.getenv("MEMORY_PRUNE_DAYS", "30"))
    MEMORY_MIN_IMPORTANCE: float = float(os.getenv("MEMORY_MIN_IMPORTANCE", "0.3"))
    MEMORY_MAX_ACCESS_COUNT: int = int(os.getenv("MEMORY_MAX_ACCESS_COUNT", "2"))
    MEMORY_MAX_PER_USER: int = int(os.getenv("MEMORY_MAX_PER_USER", "1000"))
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "TopFloor AI Platform"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Google ADK
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    ADK_APP_NAME: str = os.getenv("ADK_APP_NAME", "topfloor-ai")

    # Twelve Data
    TWELVE_DATA_API_KEY: Optional[str] = os.getenv("TWELVE_DATA_API_KEY")
    
    # Redis & Celery - Cloud Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis-12792.c274.us-east-1-3.ec2.cloud.redislabs.com")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "12792"))
    REDIS_USERNAME: str = os.getenv("REDIS_USERNAME", "default")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "false").lower() == "true"  # Changed default to false
    
    # Construct Redis URL from components
    @property
    def redis_url(self) -> str:
        """Construct Redis URL from configuration."""
        protocol = "rediss" if self.REDIS_SSL else "redis"
        if self.REDIS_PASSWORD:
            return f"{protocol}://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"{protocol}://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Legacy support for direct URL override
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    @property
    def celery_broker_url(self) -> str:
        """Get Celery broker URL."""
        return os.getenv("CELERY_BROKER_URL") or self.REDIS_URL or self.redis_url
    
    @property
    def celery_result_backend(self) -> str:
        """Get Celery result backend URL."""
        return os.getenv("CELERY_RESULT_BACKEND") or self.REDIS_URL or self.redis_url
    
    # Task Queue Settings
    TASK_MAX_RETRIES: int = int(os.getenv("TASK_MAX_RETRIES", "3"))
    TASK_RETRY_DELAY: int = int(os.getenv("TASK_RETRY_DELAY", "60"))  # seconds
    QUEUE_ENQUEUE_MAX_RETRIES: int = int(os.getenv("QUEUE_ENQUEUE_MAX_RETRIES", "3"))
    QUEUE_ENQUEUE_BASE_DELAY: float = float(os.getenv("QUEUE_ENQUEUE_BASE_DELAY", "1.0"))  # seconds
    QUEUE_ENQUEUE_MAX_DELAY: float = float(os.getenv("QUEUE_ENQUEUE_MAX_DELAY", "8.0"))  # seconds
    
    # API Base URL
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")


# Global settings instance
settings = Settings()

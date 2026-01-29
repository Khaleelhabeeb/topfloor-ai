"""
ADK Client - Wrapper for Google Agent Development Kit initialization
"""

import os
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, SessionService
from google.adk.artifacts import InMemoryArtifactService, ArtifactService
from google.adk.runners import Runner


class ADKClient:
    """
    Singleton client for ADK initialization and configuration.
    Manages session and artifact services.
    """
    
    _instance: Optional['ADKClient'] = None
    _session_service: Optional[SessionService] = None
    _artifact_service: Optional[ArtifactService] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize ADK client with services"""
        if not hasattr(self, '_initialized'):
            self._initialize_services()
            self._initialized = True
    
    def _initialize_services(self):
        """Initialize session and artifact services"""
        # For demo mode: use in-memory services (stateless)
        # TODO: Switch to VertexAiSessionService for production
        self._session_service = InMemorySessionService()
        self._artifact_service = InMemoryArtifactService()
    
    @property
    def session_service(self) -> SessionService:
        """Get session service instance"""
        return self._session_service
    
    @property
    def artifact_service(self) -> ArtifactService:
        """Get artifact service instance"""
        return self._artifact_service
    
    def create_runner(self, agent: LlmAgent, app_name: str = "topfloor-ai") -> Runner:
        """
        Create a runner for agent execution
        
        Args:
            agent: The root agent to run
            app_name: Application name for session tracking
            
        Returns:
            Configured Runner instance
        """
        return Runner(
            agent=agent,
            session_service=self.session_service,
            artifact_service=self.artifact_service,
            app_name=app_name
        )
    
    def get_api_key(self) -> str:
        """
        Get Google API key from environment
        
        Returns:
            API key string
            
        Raises:
            ValueError: If API key not found
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment. "
                "Please set it in .env file or environment variables."
            )
        return api_key
    
    def validate_configuration(self) -> bool:
        """
        Validate ADK configuration
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check API key
        self.get_api_key()
        
        # Check services are initialized
        if not self._session_service:
            raise ValueError("Session service not initialized")
        if not self._artifact_service:
            raise ValueError("Artifact service not initialized")
        
        return True


# Global client instance
adk_client = ADKClient()

"""
ADK Runner - Handles agent execution with proper session management
"""

from typing import Optional, Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import Session as ADKSession
from google import genai
import asyncio

from app.adk.client import adk_client


class AgentRunner:
    """
    Wrapper for ADK Runner with session management.
    Handles agent execution and response processing.
    """
    
    def __init__(
        self,
        agent: LlmAgent,
        session_id: str,
        user_id: int,
        app_name: str = "topfloor-ai"
    ):
        """
        Initialize agent runner.
        
        Args:
            agent: The root agent to run
            session_id: Session ID for tracking (database session)
            user_id: User ID for tracking
            app_name: Application name
        """
        self.agent = agent
        self.db_session_id = session_id  # Database session ID for tracking
        self.user_id = str(user_id)  # ADK expects string user_id
        self.app_name = app_name
        self.runner = adk_client.create_runner(agent, app_name)
        self._adk_session_id: Optional[str] = None
    
    def _ensure_adk_session(self) -> str:
        """
        Ensure an ADK session exists and return its ID.
        Creates one if it doesn't exist.
        
        Returns:
            ADK session ID
        """
        if self._adk_session_id:
            return self._adk_session_id
        
        # Create ADK session using the sync method
        session = adk_client.session_service.create_session_sync(
            app_name=self.app_name,
            user_id=self.user_id,
            state={"db_session_id": self.db_session_id}
        )
        self._adk_session_id = session.id
        return self._adk_session_id
    
    async def _ensure_adk_session_async(self) -> str:
        """
        Ensure an ADK session exists and return its ID (async version).
        Creates one if it doesn't exist.
        
        Returns:
            ADK session ID
        """
        if self._adk_session_id:
            return self._adk_session_id
        
        # Create ADK session
        session = await adk_client.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            state={"db_session_id": self.db_session_id}
        )
        self._adk_session_id = session.id
        return self._adk_session_id
    
    def run(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute agent with a message synchronously.
        
        Args:
            message: User message to send to agent
            context: Optional context dictionary
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Ensure we have an ADK session
            adk_session_id = self._ensure_adk_session()
            
            # Create content from message
            content = genai.types.Content(
                parts=[genai.types.Part(text=message)]
            )
            
            # Run agent with session_id
            response_events = list(self.runner.run(
                user_id=self.user_id,
                session_id=adk_session_id,
                new_message=content
            ))
            
            # Process response events
            response_text = self._process_response_events(response_events)
            
            return {
                "response": response_text,
                "session_id": self.db_session_id,  # Return DB session_id for tracking
                "events_count": len(response_events),
                "context": context
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            raise RuntimeError(f"Agent execution failed: {str(e)}\nDetails: {error_details}")
    
    async def run_async(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute agent with a message asynchronously.
        
        Args:
            message: User message to send to agent
            context: Optional context dictionary
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Ensure we have an ADK session
            adk_session_id = await self._ensure_adk_session_async()
            
            # Create content from message
            content = genai.types.Content(
                parts=[genai.types.Part(text=message)]
            )
            
            # Run agent with session_id
            response_events = []
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=adk_session_id,
                new_message=content
            ):
                response_events.append(event)
            
            # Process response events
            response_text = self._process_response_events(response_events)
            
            return {
                "response": response_text,
                "session_id": self.db_session_id,  # Return DB session_id for tracking
                "events_count": len(response_events),
                "context": context
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            raise RuntimeError(f"Agent execution failed: {str(e)}\nDetails: {error_details}")
    
    def _process_response_events(self, events: List[Any]) -> str:
        """
        Process response events and extract text.
        
        Args:
            events: List of response events from runner
            
        Returns:
            Extracted response text
        """
        response_parts = []
        
        for event in events:
            # Extract text from event
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_parts.append(part.text)
        
        # Join all parts
        response_text = "\n".join(response_parts) if response_parts else "No response generated"
        
        return response_text
    
    def get_session(self) -> Optional[ADKSession]:
        """
        Get the current ADK session.
        
        Returns:
            ADK Session object or None
        """
        if not self._adk_session_id:
            return None
        try:
            return adk_client.session_service.get_session_sync(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self._adk_session_id
            )
        except Exception:
            return None
    
    @property
    def session_id(self) -> str:
        """Get the database session ID for tracking."""
        return self.db_session_id
    
    @property
    def adk_session_id(self) -> Optional[str]:
        """Get the ADK session ID if created."""
        return self._adk_session_id

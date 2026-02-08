"""
ADK Runner - Handles agent execution with proper session management
"""

from typing import Optional, Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import Session as ADKSession
from google import genai
import asyncio
import os

from app.adk.client import adk_client
from app.services.memory_service import get_memory_service


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
        app_name: str = "topfloor-ai",
        agent_type: Optional[str] = None,
        enable_memory: bool = None
    ):
        """
        Initialize agent runner.
        
        Args:
            agent: The root agent to run
            session_id: Session ID for tracking (database session)
            user_id: User ID for tracking
            app_name: Application name
            agent_type: Type of agent (finance, data_analyst, researcher, team_lead)
            enable_memory: Whether to enable automatic memory storage/retrieval (defaults to MEMORY_ENABLED env var)
        """
        self.agent = agent
        self.db_session_id = session_id  # Database session ID for tracking
        self.user_id = str(user_id)  # ADK expects string user_id
        self.user_id_int = user_id  # Keep integer version for memory service
        self.app_name = app_name
        self.agent_type = agent_type
        
        # Check environment variable if enable_memory not explicitly set
        if enable_memory is None:
            enable_memory = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
        
        self.enable_memory = enable_memory
        self.runner = adk_client.create_runner(agent, app_name)
        self._adk_session_id: Optional[str] = None
        
        # Initialize memory service if enabled
        if self.enable_memory:
            try:
                self.memory_service = get_memory_service()
            except Exception as e:
                print(f"Warning: Failed to initialize memory service: {e}")
                self.enable_memory = False
    
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
            # Retrieve relevant memories if enabled
            relevant_memories = []
            if self.enable_memory and self.agent_type:
                relevant_memories = self.memory_service.search(
                    query=message,
                    user_id=self.user_id_int,
                    agent_type=self.agent_type,
                    limit=3
                )
            
            # Ensure we have an ADK session
            adk_session_id = self._ensure_adk_session()
            
            # Augment message with relevant memories
            augmented_message = self._augment_message_with_memories(message, relevant_memories)
            
            # Create content from message
            content = genai.types.Content(
                parts=[genai.types.Part(text=augmented_message)]
            )
            
            # Run agent with session_id
            response_events = list(self.runner.run(
                user_id=self.user_id,
                session_id=adk_session_id,
                new_message=content
            ))
            
            # Process response events
            response_text = self._process_response_events(response_events)
            
            # Store important information in memory if enabled
            if self.enable_memory and self.agent_type:
                self._store_interaction_memory(message, response_text)
            
            return {
                "response": response_text,
                "session_id": self.db_session_id,  # Return DB session_id for tracking
                "events_count": len(response_events),
                "context": context,
                "memories_used": len(relevant_memories)
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
            # Retrieve relevant memories if enabled
            relevant_memories = []
            if self.enable_memory and self.agent_type:
                relevant_memories = self.memory_service.search(
                    query=message,
                    user_id=self.user_id_int,
                    agent_type=self.agent_type,
                    limit=3
                )
            
            # Ensure we have an ADK session
            adk_session_id = await self._ensure_adk_session_async()
            
            # Augment message with relevant memories
            augmented_message = self._augment_message_with_memories(message, relevant_memories)
            
            # Create content from message
            content = genai.types.Content(
                parts=[genai.types.Part(text=augmented_message)]
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
            
            # Store important information in memory if enabled
            if self.enable_memory and self.agent_type:
                self._store_interaction_memory(message, response_text)
            
            return {
                "response": response_text,
                "session_id": self.db_session_id,  # Return DB session_id for tracking
                "events_count": len(response_events),
                "context": context,
                "memories_used": len(relevant_memories)
            }
            
        except Exception as e:
            import traceback
            from app.core.mock_responses import should_use_mock_response, get_mock_agent_response, log_mock_usage
            
            error_details = traceback.format_exc()
            error_message = str(e)
            
            # Check if we should use mock response for rate limit errors
            if should_use_mock_response(error_message):
                log_mock_usage(self.agent_type or "unknown", error_message)
                mock_response = get_mock_agent_response(self.agent_type or "unknown", message)
                
                return {
                    "response": mock_response["response"],
                    "session_id": self.db_session_id,
                    "events_count": 0,
                    "context": context,
                    "memories_used": 0,
                    "metadata": mock_response["metadata"]
                }
            
            # If not a rate limit error or mocking is disabled, raise the original error
            raise RuntimeError(f"Agent execution failed: {error_message}\nDetails: {error_details}")
    
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
    
    def _augment_message_with_memories(self, message: str, memories: List[Any]) -> str:
        """
        Augment user message with relevant memories.
        
        Args:
            message: Original user message
            memories: List of relevant Memory objects
            
        Returns:
            Augmented message with memory context
        """
        if not memories:
            return message
        
        # Build memory context
        memory_context = "\n\n[Relevant Context from Past Interactions]:\n"
        for i, memory in enumerate(memories, 1):
            memory_context += f"{i}. {memory.content}\n"
        
        # Prepend memory context to message
        return f"{memory_context}\n[Current User Message]:\n{message}"
    
    def _store_interaction_memory(self, user_message: str, agent_response: str) -> None:
        """
        Store important information from the interaction in long-term memory.
        
        Args:
            user_message: User's message
            agent_response: Agent's response
        """
        try:
            # Extract and store important information
            # For now, store user preferences and key facts mentioned
            
            # Check if user is expressing a preference
            preference_keywords = ["prefer", "like", "want", "need", "always", "never", "usually"]
            if any(keyword in user_message.lower() for keyword in preference_keywords):
                self.memory_service.store(
                    user_id=self.user_id_int,
                    agent_type=self.agent_type,
                    content=f"User preference: {user_message}",
                    importance=0.8,
                    memory_type="preference",
                    tags=["preference", "user-stated"]
                )
            
            # Store important decisions or facts from longer responses
            if len(agent_response) > 200:
                # Extract first sentence or summary
                summary = agent_response.split('.')[0] + '.'
                if len(summary) > 50:  # Only store if meaningful
                    self.memory_service.store(
                        user_id=self.user_id_int,
                        agent_type=self.agent_type,
                        content=f"Discussion summary: {summary}",
                        importance=0.6,
                        memory_type="summary",
                        tags=["interaction", "summary"]
                    )
        except Exception:
            # Silently fail on memory storage errors
            pass

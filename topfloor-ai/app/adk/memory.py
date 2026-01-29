"""
ADK Memory Management - Strategy for handling agent memory without bloat
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from google.adk.sessions import Session as ADKSession


class MemoryStrategy:
    """
    Memory management strategy for ADK sessions.
    
    Goals:
    - Prevent memory bloat by not storing raw conversation history in DB
    - Use ADK's session.state for short-term task context
    - Store only metadata and references in database
    - Implement memory scoping per user + agent + session
    
    Memory Layers:
    1. Short-term (ADK session.state): Current task context, temporary data
    2. Metadata (Database): Session info, status, timestamps
    3. Long-term (Future): Summarized intent, preferences (not implemented yet)
    """
    
    @staticmethod
    def initialize_session_state(
        adk_session: ADKSession,
        user_id: int,
        agent_type: str,
        initial_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize session state with proper scoping.
        
        Args:
            adk_session: ADK session to initialize
            user_id: User ID for scoping
            agent_type: Agent type for scoping
            initial_context: Optional initial context data
        """
        # Initialize base state structure
        base_state = {
            "user_id": user_id,
            "agent_type": agent_type,
            "session_started_at": datetime.now(timezone.utc).isoformat(),
            "task_context": {},
            "metadata": {},
        }
        
        # Merge with initial context if provided
        if initial_context:
            base_state.update(initial_context)
        
        # Set state on ADK session
        if hasattr(adk_session, 'state'):
            adk_session.state.update(base_state)
    
    @staticmethod
    def update_task_context(
        adk_session: ADKSession,
        context_updates: Dict[str, Any]
    ):
        """
        Update the task context in session state.
        
        Args:
            adk_session: ADK session
            context_updates: Context updates to apply
        """
        if hasattr(adk_session, 'state'):
            if "task_context" not in adk_session.state:
                adk_session.state["task_context"] = {}
            
            adk_session.state["task_context"].update(context_updates)
    
    @staticmethod
    def get_task_context(
        adk_session: ADKSession
    ) -> Dict[str, Any]:
        """
        Get the current task context from session state.
        
        Args:
            adk_session: ADK session
            
        Returns:
            Task context dictionary
        """
        if hasattr(adk_session, 'state'):
            return adk_session.state.get("task_context", {})
        return {}
    
    @staticmethod
    def clear_task_context(adk_session: ADKSession):
        """
        Clear the task context (useful for starting new tasks).
        
        Args:
            adk_session: ADK session
        """
        if hasattr(adk_session, 'state'):
            adk_session.state["task_context"] = {}
    
    @staticmethod
    def add_metadata(
        adk_session: ADKSession,
        key: str,
        value: Any
    ):
        """
        Add metadata to session state.
        
        Args:
            adk_session: ADK session
            key: Metadata key
            value: Metadata value
        """
        if hasattr(adk_session, 'state'):
            if "metadata" not in adk_session.state:
                adk_session.state["metadata"] = {}
            
            adk_session.state["metadata"][key] = value
    
    @staticmethod
    def get_metadata(
        adk_session: ADKSession,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get metadata from session state.
        
        Args:
            adk_session: ADK session
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        if hasattr(adk_session, 'state'):
            metadata = adk_session.state.get("metadata", {})
            return metadata.get(key, default)
        return default
    
    @staticmethod
    def get_session_summary(adk_session: ADKSession) -> Dict[str, Any]:
        """
        Get a summary of the session state (for debugging/monitoring).
        
        Args:
            adk_session: ADK session
            
        Returns:
            Summary dictionary
        """
        if not hasattr(adk_session, 'state'):
            return {}
        
        state = adk_session.state
        
        return {
            "user_id": state.get("user_id"),
            "agent_type": state.get("agent_type"),
            "session_started_at": state.get("session_started_at"),
            "task_context_keys": list(state.get("task_context", {}).keys()),
            "metadata_keys": list(state.get("metadata", {}).keys()),
            "state_size_estimate": len(str(state))  # Rough estimate
        }
    
    @staticmethod
    def enforce_memory_limits(
        adk_session: ADKSession,
        max_task_context_items: int = 50,
        max_metadata_items: int = 100
    ) -> Dict[str, int]:
        """
        Enforce memory limits to prevent bloat.
        
        Args:
            adk_session: ADK session
            max_task_context_items: Max items in task context
            max_metadata_items: Max items in metadata
            
        Returns:
            Dictionary with counts of items removed
        """
        removed = {"task_context": 0, "metadata": 0}
        
        if not hasattr(adk_session, 'state'):
            return removed
        
        # Limit task context
        task_context = adk_session.state.get("task_context", {})
        if len(task_context) > max_task_context_items:
            # Keep only the most recent items (assuming dict maintains insertion order)
            items = list(task_context.items())
            kept_items = dict(items[-max_task_context_items:])
            removed["task_context"] = len(task_context) - len(kept_items)
            adk_session.state["task_context"] = kept_items
        
        # Limit metadata
        metadata = adk_session.state.get("metadata", {})
        if len(metadata) > max_metadata_items:
            items = list(metadata.items())
            kept_items = dict(items[-max_metadata_items:])
            removed["metadata"] = len(metadata) - len(kept_items)
            adk_session.state["metadata"] = kept_items
        
        return removed


class MemoryScope:
    """
    Helper class for managing memory scoping.
    
    Memory is scoped by:
    - User ID: Isolate users from each other
    - Agent Type: Different agents have different contexts
    - Session ID: Each conversation is isolated
    """
    
    @staticmethod
    def create_scope_key(
        user_id: int,
        agent_type: str,
        session_id: str
    ) -> str:
        """
        Create a scoped key for memory storage.
        
        Args:
            user_id: User ID
            agent_type: Agent type
            session_id: Session ID
            
        Returns:
            Scoped key string
        """
        return f"user_{user_id}:agent_{agent_type}:session_{session_id}"
    
    @staticmethod
    def parse_scope_key(scope_key: str) -> Optional[Dict[str, str]]:
        """
        Parse a scope key back into components.
        
        Args:
            scope_key: Scoped key string
            
        Returns:
            Dictionary with user_id, agent_type, session_id or None if invalid
        """
        try:
            parts = scope_key.split(":")
            if len(parts) != 3:
                return None
            
            user_part = parts[0].replace("user_", "")
            agent_part = parts[1].replace("agent_", "")
            session_part = parts[2].replace("session_", "")
            
            return {
                "user_id": user_part,
                "agent_type": agent_part,
                "session_id": session_part
            }
        except Exception:
            return None
    
    @staticmethod
    def validate_scope(
        user_id: int,
        agent_type: str,
        session_id: str
    ) -> bool:
        """
        Validate that scope parameters are valid.
        
        Args:
            user_id: User ID
            agent_type: Agent type
            session_id: Session ID
            
        Returns:
            True if valid, False otherwise
        """
        return (
            user_id > 0 and
            len(agent_type) > 0 and
            len(session_id) > 0
        )

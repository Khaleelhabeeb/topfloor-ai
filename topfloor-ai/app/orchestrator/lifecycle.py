"""
Agent Lifecycle Management - Track and manage agent execution lifecycle
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum


class AgentExecutionStatus(str, Enum):
    """Status of agent execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentExecution:
    """
    Represents a single agent execution.
    
    Tracks the lifecycle of an agent's execution including:
    - Start/end times
    - Status
    - Input/output
    - Errors
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_type: str,
        user_id: int,
        session_id: str
    ):
        """
        Initialize agent execution.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of agent
            user_id: User ID
            session_id: Session ID
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.user_id = user_id
        self.session_id = session_id
        
        self.status = AgentExecutionStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.duration_seconds: Optional[float] = None
        
        self.input_data: Optional[Dict[str, Any]] = None
        self.output_data: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        
        self.metadata: Dict[str, Any] = {}
    
    def start(self, input_data: Optional[Dict[str, Any]] = None):
        """
        Mark execution as started.
        
        Args:
            input_data: Optional input data for the agent
        """
        self.status = AgentExecutionStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self.input_data = input_data
    
    def complete(self, output_data: Optional[Dict[str, Any]] = None):
        """
        Mark execution as completed.
        
        Args:
            output_data: Optional output data from the agent
        """
        self.status = AgentExecutionStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.output_data = output_data
        
        if self.started_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()
    
    def fail(self, error: str):
        """
        Mark execution as failed.
        
        Args:
            error: Error message
        """
        self.status = AgentExecutionStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error = error
        
        if self.started_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()
    
    def cancel(self):
        """Mark execution as cancelled"""
        self.status = AgentExecutionStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)
        
        if self.started_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()
    
    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to execution.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "metadata": self.metadata
        }


class ExecutionTracker:
    """
    Tracks agent executions across sessions.
    
    Provides observability into agent behavior and performance.
    """
    
    def __init__(self):
        """Initialize execution tracker"""
        self.executions: List[AgentExecution] = []
        self._active_executions: Dict[str, AgentExecution] = {}  # execution_id -> execution
    
    def start_execution(
        self,
        agent_name: str,
        agent_type: str,
        user_id: int,
        session_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start tracking a new agent execution.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of agent
            user_id: User ID
            session_id: Session ID
            input_data: Optional input data
            
        Returns:
            Execution ID
        """
        execution = AgentExecution(
            agent_name=agent_name,
            agent_type=agent_type,
            user_id=user_id,
            session_id=session_id
        )
        execution.start(input_data)
        
        # Generate execution ID
        execution_id = f"{session_id}_{agent_name}_{len(self.executions)}"
        
        self.executions.append(execution)
        self._active_executions[execution_id] = execution
        
        return execution_id
    
    def complete_execution(
        self,
        execution_id: str,
        output_data: Optional[Dict[str, Any]] = None
    ):
        """
        Mark an execution as completed.
        
        Args:
            execution_id: Execution ID
            output_data: Optional output data
        """
        if execution_id in self._active_executions:
            execution = self._active_executions[execution_id]
            execution.complete(output_data)
            del self._active_executions[execution_id]
    
    def fail_execution(self, execution_id: str, error: str):
        """
        Mark an execution as failed.
        
        Args:
            execution_id: Execution ID
            error: Error message
        """
        if execution_id in self._active_executions:
            execution = self._active_executions[execution_id]
            execution.fail(error)
            del self._active_executions[execution_id]
    
    def get_execution(self, execution_id: str) -> Optional[AgentExecution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            AgentExecution or None if not found
        """
        return self._active_executions.get(execution_id)
    
    def get_session_executions(self, session_id: str) -> List[AgentExecution]:
        """
        Get all executions for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of executions
        """
        return [
            exec for exec in self.executions
            if exec.session_id == session_id
        ]
    
    def get_agent_executions(
        self,
        agent_name: str,
        user_id: Optional[int] = None
    ) -> List[AgentExecution]:
        """
        Get all executions for a specific agent.
        
        Args:
            agent_name: Agent name
            user_id: Optional user ID filter
            
        Returns:
            List of executions
        """
        executions = [
            exec for exec in self.executions
            if exec.agent_name == agent_name
        ]
        
        if user_id is not None:
            executions = [
                exec for exec in executions
                if exec.user_id == user_id
            ]
        
        return executions
    
    def get_statistics(
        self,
        agent_name: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Args:
            agent_name: Optional agent name filter
            user_id: Optional user ID filter
            
        Returns:
            Statistics dictionary
        """
        executions = self.executions
        
        if agent_name:
            executions = [e for e in executions if e.agent_name == agent_name]
        if user_id is not None:
            executions = [e for e in executions if e.user_id == user_id]
        
        if not executions:
            return {
                "total_executions": 0,
                "completed": 0,
                "failed": 0,
                "cancelled": 0,
                "average_duration_seconds": 0
            }
        
        completed = [e for e in executions if e.status == AgentExecutionStatus.COMPLETED]
        failed = [e for e in executions if e.status == AgentExecutionStatus.FAILED]
        cancelled = [e for e in executions if e.status == AgentExecutionStatus.CANCELLED]
        
        durations = [e.duration_seconds for e in executions if e.duration_seconds is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_executions": len(executions),
            "completed": len(completed),
            "failed": len(failed),
            "cancelled": len(cancelled),
            "average_duration_seconds": avg_duration
        }
    
    def clear_old_executions(self, keep_last_n: int = 100):
        """
        Clear old executions to prevent memory bloat.
        
        Args:
            keep_last_n: Number of recent executions to keep
        """
        if len(self.executions) > keep_last_n:
            self.executions = self.executions[-keep_last_n:]


# Global execution tracker
execution_tracker = ExecutionTracker()

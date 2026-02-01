"""
Agent Status Service - Business logic for agent status tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from app.models.agent_status import AgentStatus, AgentStatusEnum
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


class AgentStatusService:
    """Service for managing agent status with CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_status(
        self,
        user_id: int,
        agent_type: str
    ) -> AgentStatus:
        """
        Get existing agent status or create a new one if it doesn't exist.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent (finance, data_analyst, researcher, etc.)
            
        Returns:
            AgentStatus object
            
        Raises:
            ValueError: If status creation fails
        """
        # Try to get existing status
        status = self.db.query(AgentStatus).filter(
            and_(
                AgentStatus.user_id == user_id,
                AgentStatus.agent_type == agent_type
            )
        ).first()
        
        # Create if doesn't exist
        if status is None:
            status = AgentStatus(
                user_id=user_id,
                agent_type=agent_type,
                status=AgentStatusEnum.AVAILABLE,
                tasks_in_queue=0,
                last_active_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db.add(status)
            try:
                self.db.commit()
                self.db.refresh(status)
            except IntegrityError as e:
                self.db.rollback()
                raise ValueError(f"Failed to create agent status: {str(e)}")
        
        return status

    
    def get_status(
        self,
        user_id: int,
        agent_type: str
    ) -> Optional[AgentStatus]:
        """
        Get agent status for a specific user and agent type.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            AgentStatus object if found, None otherwise
        """
        return self.db.query(AgentStatus).filter(
            and_(
                AgentStatus.user_id == user_id,
                AgentStatus.agent_type == agent_type
            )
        ).first()
    
    def get_status_by_id(
        self,
        status_id: int,
        user_id: Optional[int] = None
    ) -> Optional[AgentStatus]:
        """
        Get agent status by its database ID.
        
        Args:
            status_id: Database ID of the status
            user_id: Optional user ID to filter by (for authorization)
            
        Returns:
            AgentStatus object if found, None otherwise
        """
        query = self.db.query(AgentStatus).filter(AgentStatus.id == status_id)
        
        if user_id is not None:
            query = query.filter(AgentStatus.user_id == user_id)
        
        return query.first()
    
    def get_all_statuses(
        self,
        user_id: int
    ) -> List[AgentStatus]:
        """
        Get all agent statuses for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of AgentStatus objects
        """
        return self.db.query(AgentStatus).filter(
            AgentStatus.user_id == user_id
        ).all()

    
    def set_status(
        self,
        user_id: int,
        agent_type: str,
        status: AgentStatusEnum,
        current_task_id: Optional[int] = None
    ) -> AgentStatus:
        """
        Set the status of an agent.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            status: New status to set
            current_task_id: Optional task ID if agent is busy
            
        Returns:
            Updated AgentStatus object
        """
        agent_status = self.get_or_create_status(user_id, agent_type)
        
        agent_status.status = status
        agent_status.current_task_id = current_task_id
        agent_status.last_active_at = datetime.now(timezone.utc)
        agent_status.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(agent_status)
        
        return agent_status
    
    def set_available(
        self,
        user_id: int,
        agent_type: str
    ) -> AgentStatus:
        """
        Set agent status to available (convenience method).
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Updated AgentStatus object
        """
        return self.set_status(
            user_id=user_id,
            agent_type=agent_type,
            status=AgentStatusEnum.AVAILABLE,
            current_task_id=None
        )
    
    def set_busy(
        self,
        user_id: int,
        agent_type: str,
        task_id: int
    ) -> AgentStatus:
        """
        Set agent status to busy with a specific task (convenience method).
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            task_id: ID of the task being processed
            
        Returns:
            Updated AgentStatus object
        """
        return self.set_status(
            user_id=user_id,
            agent_type=agent_type,
            status=AgentStatusEnum.BUSY,
            current_task_id=task_id
        )
    
    def set_idle(
        self,
        user_id: int,
        agent_type: str
    ) -> AgentStatus:
        """
        Set agent status to idle (convenience method).
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Updated AgentStatus object
        """
        return self.set_status(
            user_id=user_id,
            agent_type=agent_type,
            status=AgentStatusEnum.IDLE,
            current_task_id=None
        )

    
    def update_queue_length(
        self,
        user_id: int,
        agent_type: str,
        tasks_in_queue: int
    ) -> AgentStatus:
        """
        Update the number of tasks in the agent's queue.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            tasks_in_queue: Number of tasks in queue
            
        Returns:
            Updated AgentStatus object
        """
        agent_status = self.get_or_create_status(user_id, agent_type)
        
        agent_status.tasks_in_queue = tasks_in_queue
        agent_status.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(agent_status)
        
        return agent_status
    
    def increment_queue(
        self,
        user_id: int,
        agent_type: str
    ) -> AgentStatus:
        """
        Increment the queue length by 1 (convenience method).
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Updated AgentStatus object
        """
        agent_status = self.get_or_create_status(user_id, agent_type)
        
        agent_status.tasks_in_queue += 1
        agent_status.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(agent_status)
        
        return agent_status
    
    def decrement_queue(
        self,
        user_id: int,
        agent_type: str
    ) -> AgentStatus:
        """
        Decrement the queue length by 1 (convenience method).
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Updated AgentStatus object
        """
        agent_status = self.get_or_create_status(user_id, agent_type)
        
        # Ensure queue doesn't go below 0
        if agent_status.tasks_in_queue > 0:
            agent_status.tasks_in_queue -= 1
        
        agent_status.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(agent_status)
        
        return agent_status

    
    def update_last_active(
        self,
        user_id: int,
        agent_type: str
    ) -> AgentStatus:
        """
        Update the last active timestamp for an agent.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Updated AgentStatus object
        """
        agent_status = self.get_or_create_status(user_id, agent_type)
        
        agent_status.last_active_at = datetime.now(timezone.utc)
        agent_status.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(agent_status)
        
        return agent_status
    
    def is_available(
        self,
        user_id: int,
        agent_type: str
    ) -> bool:
        """
        Check if an agent is available.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            True if agent is available, False otherwise
        """
        status = self.get_status(user_id, agent_type)
        
        if status is None:
            return True  # If no status exists, agent is available
        
        return status.status == AgentStatusEnum.AVAILABLE
    
    def is_busy(
        self,
        user_id: int,
        agent_type: str
    ) -> bool:
        """
        Check if an agent is busy.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            True if agent is busy, False otherwise
        """
        status = self.get_status(user_id, agent_type)
        
        if status is None:
            return False
        
        return status.status == AgentStatusEnum.BUSY
    
    def get_current_task(
        self,
        user_id: int,
        agent_type: str
    ) -> Optional[int]:
        """
        Get the current task ID for an agent.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Task ID if agent is busy, None otherwise
        """
        status = self.get_status(user_id, agent_type)
        
        if status is None:
            return None
        
        return status.current_task_id
    
    def get_queue_length(
        self,
        user_id: int,
        agent_type: str
    ) -> int:
        """
        Get the number of tasks in the agent's queue.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Number of tasks in queue
        """
        status = self.get_status(user_id, agent_type)
        
        if status is None:
            return 0
        
        return status.tasks_in_queue

    
    def get_available_agents(
        self,
        user_id: int
    ) -> List[AgentStatus]:
        """
        Get all available agents for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of available AgentStatus objects
        """
        return self.db.query(AgentStatus).filter(
            and_(
                AgentStatus.user_id == user_id,
                AgentStatus.status == AgentStatusEnum.AVAILABLE
            )
        ).all()
    
    def get_busy_agents(
        self,
        user_id: int
    ) -> List[AgentStatus]:
        """
        Get all busy agents for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of busy AgentStatus objects
        """
        return self.db.query(AgentStatus).filter(
            and_(
                AgentStatus.user_id == user_id,
                AgentStatus.status == AgentStatusEnum.BUSY
            )
        ).all()
    
    def get_status_summary(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get a summary of all agent statuses for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with status summary
        """
        all_statuses = self.get_all_statuses(user_id)
        
        summary = {
            "total_agents": len(all_statuses),
            "available": 0,
            "busy": 0,
            "idle": 0,
            "total_tasks_in_queue": 0,
            "agents": []
        }
        
        for status in all_statuses:
            # Count by status
            if status.status == AgentStatusEnum.AVAILABLE:
                summary["available"] += 1
            elif status.status == AgentStatusEnum.BUSY:
                summary["busy"] += 1
            elif status.status == AgentStatusEnum.IDLE:
                summary["idle"] += 1
            
            # Sum queue lengths
            summary["total_tasks_in_queue"] += status.tasks_in_queue
            
            # Add agent details
            summary["agents"].append({
                "agent_type": status.agent_type,
                "status": status.status.value,
                "current_task_id": status.current_task_id,
                "tasks_in_queue": status.tasks_in_queue,
                "last_active_at": status.last_active_at.isoformat() if status.last_active_at else None
            })
        
        return summary
    
    def delete_status(
        self,
        user_id: int,
        agent_type: str
    ) -> bool:
        """
        Delete an agent status record.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            True if status was deleted, False if not found
        """
        status = self.get_status(user_id, agent_type)
        
        if status is None:
            return False
        
        self.db.delete(status)
        self.db.commit()
        
        return True
    
    def reset_status(
        self,
        user_id: int,
        agent_type: str
    ) -> AgentStatus:
        """
        Reset an agent status to default values.
        
        Args:
            user_id: ID of the user
            agent_type: Type of agent
            
        Returns:
            Reset AgentStatus object
        """
        agent_status = self.get_or_create_status(user_id, agent_type)
        
        agent_status.status = AgentStatusEnum.AVAILABLE
        agent_status.current_task_id = None
        agent_status.tasks_in_queue = 0
        agent_status.last_active_at = datetime.now(timezone.utc)
        agent_status.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(agent_status)
        
        return agent_status

"""
Task Service - Business logic for task management
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.task_history import TaskHistory
from app.schemas.task import TaskCreate, TaskUpdate
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class TaskService:
    """Service for managing tasks with CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, user_id: int, task_data: TaskCreate) -> Task:
        """
        Create a new task for a user.
        
        Args:
            user_id: ID of the user creating the task
            task_data: Task creation data
            
        Returns:
            Created task object
            
        Raises:
            ValueError: If task creation fails
        """
        # Generate unique task_id
        task_id = f"task_{uuid.uuid4().hex[:16]}"
        
        # Create task object
        db_task = Task(
            task_id=task_id,
            user_id=user_id,
            agent_type=task_data.agent_type,
            title=task_data.title,
            description=task_data.description,
            task_type=task_data.task_type,
            priority=task_data.priority,
            status=TaskStatus.PENDING,
            input_data=task_data.input_data,
            progress=task_data.progress,
            due_date=task_data.due_date,
        )
        
        self.db.add(db_task)
        try:
            self.db.flush()
            self._add_history(
                task_id=db_task.id,
                status=db_task.status.value,
                message="Task created",
                metadata={
                    "action_type": "task_assigned",
                    "task_id": db_task.task_id,
                    "agent_type": db_task.agent_type,
                    "priority": db_task.priority.value,
                }
            )
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create task: {str(e)}")
    
    def get_task_by_id(self, task_id: int, user_id: Optional[int] = None) -> Optional[Task]:
        """
        Get a task by its database ID.
        
        Args:
            task_id: Database ID of the task
            user_id: Optional user ID to filter by (for authorization)
            
        Returns:
            Task object if found, None otherwise
        """
        query = self.db.query(Task).filter(Task.id == task_id)
        
        if user_id is not None:
            query = query.filter(Task.user_id == user_id)
        
        return query.first()
    
    def get_task_by_task_id(self, task_id: str, user_id: Optional[int] = None) -> Optional[Task]:
        """
        Get a task by its unique task_id string.
        
        Args:
            task_id: Unique task_id string
            user_id: Optional user ID to filter by (for authorization)
            
        Returns:
            Task object if found, None otherwise
        """
        query = self.db.query(Task).filter(Task.task_id == task_id)
        
        if user_id is not None:
            query = query.filter(Task.user_id == user_id)
        
        return query.first()
    
    def get_tasks(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        priority: Optional[TaskPriority] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Task], int]:
        """
        Get a list of tasks with optional filtering, sorting, and pagination.
        
        Args:
            user_id: User ID to filter tasks
            agent_type: Optional agent type filter
            status: Optional status filter
            task_type: Optional task type filter
            priority: Optional priority filter
            sort_by: Field to sort by (created_at, updated_at, priority, status, title)
            sort_order: Sort order (asc or desc)
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of tasks, total count)
        """
        # Build base query
        query = self.db.query(Task).filter(Task.user_id == user_id)
        
        # Apply filters
        if agent_type is not None:
            query = query.filter(Task.agent_type == agent_type)
        
        if status is not None:
            query = query.filter(Task.status == status)
        
        if task_type is not None:
            query = query.filter(Task.task_type == task_type)
        
        if priority is not None:
            query = query.filter(Task.priority == priority)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Apply pagination
        tasks = query.offset(skip).limit(limit).all()
        
        return tasks, total
    
    def update_task(
        self,
        task_id: int,
        user_id: int,
        task_update: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task.
        
        Args:
            task_id: Database ID of the task
            user_id: User ID (for authorization)
            task_update: Task update data
            
        Returns:
            Updated task object if found, None otherwise
            
        Raises:
            ValueError: If update fails
        """
        # Get task
        task = self.get_task_by_id(task_id, user_id)
        
        if task is None:
            return None
        
        # Update fields
        previous_status = task.status
        previous_priority = task.priority
        previous_progress = task.progress
        previous_due_date = task.due_date
        update_data = task_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Update timestamp
        task.updated_at = datetime.utcnow()
        
        # Update lifecycle timestamps based on status changes
        if task_update.status is not None:
            if task_update.status == TaskStatus.IN_PROGRESS and task.started_at is None:
                task.started_at = datetime.utcnow()
            elif task_update.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at is None:
                    task.completed_at = datetime.utcnow()
        
        action_type = "task_updated"
        if "status" in update_data and task.status != previous_status:
            if task.status == TaskStatus.COMPLETED:
                action_type = "task_completed"
            elif task.status == TaskStatus.CANCELLED:
                action_type = "task_cancelled"

        history_message = "Task updated"
        if action_type == "task_completed":
            history_message = "Task completed"
        elif action_type == "task_cancelled":
            history_message = "Task cancelled"

        self._add_history(
            task_id=task.id,
            status=task.status.value,
            message=history_message,
            metadata={
                "action_type": action_type,
                "task_id": task.task_id,
                "agent_type": task.agent_type,
                "previous": {
                    "status": previous_status.value,
                    "priority": previous_priority.value,
                    "progress": previous_progress,
                    "due_date": previous_due_date.isoformat() if previous_due_date else None,
                },
                "updates": update_data,
            }
        )

        try:
            self.db.commit()
            self.db.refresh(task)
            return task
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update task: {str(e)}")
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Database ID of the task
            user_id: User ID (for authorization)
            
        Returns:
            True if task was deleted, False if not found
        """
        task = self.get_task_by_id(task_id, user_id)
        
        if task is None:
            return False
        
        self.db.delete(task)
        self.db.commit()
        
        return True

    def _add_history(
        self,
        task_id: int,
        status: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        history = TaskHistory(
            task_id=task_id,
            status=status,
            message=message,
            event_metadata=metadata
        )
        self.db.add(history)
    
    def update_task_status(
        self,
        task_id: int,
        user_id: int,
        status: TaskStatus,
        error_message: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update only the status of a task (convenience method).
        
        Args:
            task_id: Database ID of the task
            user_id: User ID (for authorization)
            status: New status
            error_message: Optional error message if status is FAILED
            
        Returns:
            Updated task object if found, None otherwise
        """
        task_update = TaskUpdate(status=status, error_message=error_message)
        return self.update_task(task_id, user_id, task_update)
    
    def update_task_result(
        self,
        task_id: int,
        user_id: int,
        result_data: Dict[str, Any]
    ) -> Optional[Task]:
        """
        Update the result data of a task (convenience method).
        
        Args:
            task_id: Database ID of the task
            user_id: User ID (for authorization)
            result_data: Result data to store
            
        Returns:
            Updated task object if found, None otherwise
        """
        task_update = TaskUpdate(result_data=result_data)
        return self.update_task(task_id, user_id, task_update)
    
    def get_agent_tasks(
        self,
        user_id: int,
        agent_type: str,
        status: Optional[TaskStatus] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Task], int]:
        """
        Get tasks for a specific agent (convenience method).
        
        Args:
            user_id: User ID to filter tasks
            agent_type: Agent type to filter
            status: Optional status filter
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of tasks, total count)
        """
        return self.get_tasks(
            user_id=user_id,
            agent_type=agent_type,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
    
    def get_pending_tasks(
        self,
        user_id: int,
        agent_type: Optional[str] = None
    ) -> List[Task]:
        """
        Get all pending tasks, optionally filtered by agent.
        
        Args:
            user_id: User ID to filter tasks
            agent_type: Optional agent type filter
            
        Returns:
            List of pending tasks ordered by priority and creation time
        """
        query = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.status == TaskStatus.PENDING
            )
        )
        
        if agent_type is not None:
            query = query.filter(Task.agent_type == agent_type)
        
        # Order by priority (critical first) and creation time
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        tasks = query.all()
        tasks.sort(key=lambda t: (priority_order.get(t.priority, 999), t.created_at))
        
        return tasks
    
    def count_tasks_by_status(
        self,
        user_id: int,
        agent_type: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Count tasks by status for a user.
        
        Args:
            user_id: User ID to filter tasks
            agent_type: Optional agent type filter
            
        Returns:
            Dictionary mapping status to count
        """
        query = self.db.query(Task).filter(Task.user_id == user_id)
        
        if agent_type is not None:
            query = query.filter(Task.agent_type == agent_type)
        
        tasks = query.all()
        
        counts = {status.value: 0 for status in TaskStatus}
        for task in tasks:
            counts[task.status.value] += 1
        
        return counts

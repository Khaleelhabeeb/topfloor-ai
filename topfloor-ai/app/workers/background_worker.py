"""
Background Worker - Celery tasks for background processing
Handles task processing with FIFO queuing per agent and priority handling
"""

from celery import Task
from typing import Dict, Any, Optional
import socket
from urllib.parse import urlparse
import traceback
from datetime import datetime
import random
import time

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.task import Task as TaskModel, TaskStatus, TaskPriority
from app.models.task_history import TaskHistory
from app.services.task_service import TaskService
from app.services.agent_status_service import AgentStatusService
from app.services.websocket_service import connection_manager
from app.agents.factory import AgentFactory
from app.adk.runner import AgentRunner
import asyncio


class TaskProcessor:
    """
    Processes tasks by executing agents and managing task lifecycle.
    """
    
    def __init__(self, db_session):
        self.db = db_session
        self.task_service = TaskService(db_session)
        self.agent_status_service = AgentStatusService(db_session)
        self.agent_factory = AgentFactory()
    
    def process_task(self, task_id: int) -> Dict[str, Any]:
        """
        Process a single task by executing the assigned agent.
        
        Args:
            task_id: Database ID of the task to process
            
        Returns:
            Dictionary with processing results
            
        Raises:
            Exception: If task processing fails
        """
        # Load task from database
        task = self.task_service.get_task_by_id(task_id)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update status to in_progress
        self._update_task_status(
            task,
            TaskStatus.IN_PROGRESS,
            "Task processing started"
        )
        
        # Update agent status to busy
        agent_status = self.agent_status_service.set_busy(
            user_id=task.user_id,
            agent_type=task.agent_type,
            task_id=task.id
        )
        
        # Broadcast agent status change
        self._broadcast_agent_status(
            user_id=task.user_id,
            agent_type=task.agent_type,
            status=agent_status.status.value,
            current_task_id=task.id,
            tasks_in_queue=agent_status.tasks_in_queue
        )
        
        # Broadcast task status change
        self._broadcast_task_status(
            user_id=task.user_id,
            task_id=task.task_id,
            agent_type=task.agent_type,
            status=TaskStatus.IN_PROGRESS.value,
            message="Task processing started"
        )
        
        try:
            # Execute agent
            result = self._execute_agent(task)
            
            # Store results
            task.result_data = result
            task.status = TaskStatus.COMPLETED
            task.progress = max(task.progress or 0, 100)
            task.completed_at = datetime.utcnow()
            self.db.commit()
            
            # Log completion
            self._add_task_history(
                task,
                TaskStatus.COMPLETED,
                "Task completed successfully"
            )
            
            # Broadcast task completion
            self._broadcast_task_completion(
                user_id=task.user_id,
                task_id=task.task_id,
                agent_type=task.agent_type,
                success=True,
                result=result
            )
            
            return {
                "success": True,
                "task_id": task.task_id,
                "result": result
            }
            
        except Exception as e:
            # Handle failure
            error_message = str(e)
            error_trace = traceback.format_exc()
            
            task.status = TaskStatus.FAILED
            task.progress = max(task.progress or 0, 100)
            task.error_message = f"{error_message}\n\nTraceback:\n{error_trace}"
            task.completed_at = datetime.utcnow()
            self.db.commit()
            
            # Log failure
            self._add_task_history(
                task,
                TaskStatus.FAILED,
                f"Task failed: {error_message}"
            )
            
            # Broadcast task completion (failure)
            self._broadcast_task_completion(
                user_id=task.user_id,
                task_id=task.task_id,
                agent_type=task.agent_type,
                success=False,
                error=error_message
            )
            
            return {
                "success": False,
                "task_id": task.task_id,
                "error": error_message
            }
            
        finally:
            # Update agent status back to available
            agent_status = self.agent_status_service.set_available(
                user_id=task.user_id,
                agent_type=task.agent_type
            )
            
            # Decrement queue count
            agent_status = self.agent_status_service.decrement_queue(
                user_id=task.user_id,
                agent_type=task.agent_type
            )
            
            # Broadcast agent status change
            self._broadcast_agent_status(
                user_id=task.user_id,
                agent_type=task.agent_type,
                status=agent_status.status.value,
                current_task_id=None,
                tasks_in_queue=agent_status.tasks_in_queue
            )
            
            # Broadcast queue update
            self._broadcast_queue_update(
                user_id=task.user_id,
                agent_type=task.agent_type,
                tasks_in_queue=agent_status.tasks_in_queue
            )
    
    def _execute_agent(self, task: TaskModel) -> Dict[str, Any]:
        """
        Execute the agent for the given task.
        
        Args:
            task: Task model to execute
            
        Returns:
            Agent execution result
        """
        # Create agent
        agent = self.agent_factory.create_agent(task.agent_type)
        
        # Create session ID for tracking
        session_id = f"task_{task.task_id}"
        
        # Create agent runner
        runner = AgentRunner(
            agent=agent,
            session_id=session_id,
            user_id=task.user_id,
            agent_type=task.agent_type,
            enable_memory=True
        )
        
        # Prepare message from task description and input data
        message = task.description
        if task.input_data:
            message += f"\n\nAdditional Context:\n{task.input_data}"
        
        # Execute agent
        result = runner.run(message=message, context=task.input_data)
        
        return result
    
    def _update_task_status(
        self,
        task: TaskModel,
        status: TaskStatus,
        message: str
    ):
        """Update task status and add history entry."""
        task.status = status
        task.updated_at = datetime.utcnow()

        if status == TaskStatus.QUEUED:
            task.progress = max(task.progress or 0, 10)
        elif status == TaskStatus.IN_PROGRESS:
            task.progress = max(task.progress or 0, 50)
        
        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        
        self.db.commit()
        self._add_task_history(task, status, message)
    
    def _add_task_history(
        self,
        task: TaskModel,
        status: TaskStatus,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a history entry for the task."""
        history = TaskHistory(
            task_id=task.id,
            status=status,
            message=message,
            event_metadata=metadata
        )
        self.db.add(history)
        self.db.commit()
    
    def _process_next_task_in_queue(self, user_id: int, agent_type: str):
        """
        Check if there are more pending tasks for this agent and process them.
        
        Args:
            user_id: User ID
            agent_type: Agent type
        """
        # Get next pending task for this agent
        pending_tasks = self.task_service.get_pending_tasks(
            user_id=user_id,
            agent_type=agent_type
        )
        if pending_tasks:
            # Get the first pending task (highest priority, oldest first)
            next_task = pending_tasks[0]

            # Update status to queued
            next_task.status = TaskStatus.QUEUED
            self.db.commit()

            # Submit to Celery for processing
            process_task.delay(next_task.id)

    def _broadcast_agent_status(
        self,
        user_id: int,
        agent_type: str,
        status: str,
        current_task_id: Optional[int],
        tasks_in_queue: int
    ):
        """Broadcast agent status change via WebSocket."""
        try:
            # Try to get the running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the coroutine
                asyncio.create_task(
                    connection_manager.broadcast_agent_status_change(
                        user_id=user_id,
                        agent_type=agent_type,
                        status=status,
                        current_task_id=current_task_id,
                        tasks_in_queue=tasks_in_queue
                    )
                )
            except RuntimeError:
                # No running loop, we're in sync context - skip broadcast
                # WebSocket broadcasts will be handled by the Celery worker
                pass
        except Exception:
            # Silently fail on broadcast errors
            pass

    def _broadcast_task_status(
        self,
        user_id: int,
        task_id: str,
        agent_type: str,
        status: str,
        message: Optional[str] = None
    ):
        """Broadcast task status change via WebSocket."""
        try:
            # Try to get the running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the coroutine
                asyncio.create_task(
                    connection_manager.broadcast_task_status_change(
                        user_id=user_id,
                        task_id=task_id,
                        agent_type=agent_type,
                        status=status,
                        message_text=message
                    )
                )
            except RuntimeError:
                # No running loop, we're in sync context - skip broadcast
                # WebSocket broadcasts will be handled by the Celery worker
                pass
        except Exception:
            # Silently fail on broadcast errors
            pass
    
    def _broadcast_task_completion(
        self,
        user_id: int,
        task_id: str,
        agent_type: str,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Broadcast task completion via WebSocket."""
        try:
            # Try to get the running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the coroutine
                asyncio.create_task(
                    connection_manager.broadcast_task_completion(
                        user_id=user_id,
                        task_id=task_id,
                        agent_type=agent_type,
                        success=success,
                        result=result,
                        error=error
                    )
                )
            except RuntimeError:
                # No running loop, we're in sync context - skip broadcast
                # WebSocket broadcasts will be handled by the Celery worker
                pass
        except Exception:
            # Silently fail on broadcast errors
            pass
    
    def _broadcast_queue_update(
        self,
        user_id: int,
        agent_type: str,
        tasks_in_queue: int
    ):
        """Broadcast queue update via WebSocket."""
        try:
            # Try to get the running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the coroutine
                asyncio.create_task(
                    connection_manager.broadcast_queue_update(
                        user_id=user_id,
                        agent_type=agent_type,
                        tasks_in_queue=tasks_in_queue
                    )
                )
            except RuntimeError:
                # No running loop, we're in sync context - skip broadcast
                # WebSocket broadcasts will be handled by the Celery worker
                pass
        except Exception:
            # Silently fail on broadcast errors
            pass


def _broker_reachable(broker_url: str, timeout: float = 1.0) -> bool:
    if not broker_url:
        return False

    parsed = urlparse(broker_url)
    host = parsed.hostname
    if not host:
        return False

    if parsed.port:
        port = parsed.port
    elif parsed.scheme in {"redis", "rediss"}:
        port = 6379
    else:
        port = 5672

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


class AgentQueueManager:
    """
    Manages FIFO queues per agent with priority handling.
    """
    
    def __init__(self, db_session):
        self.db = db_session
        self.task_service = TaskService(db_session)
        self.agent_status_service = AgentStatusService(db_session)
    
    def enqueue_task(self, task_id: int) -> Dict[str, Any]:
        """
        Add a task to the agent's queue and start processing.
        
        Args:
            task_id: Database ID of the task to enqueue
            
        Returns:
            Dictionary with queue status
        """
        # Load task
        task = self.task_service.get_task_by_id(task_id)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.status in {TaskStatus.QUEUED, TaskStatus.IN_PROGRESS}:
            return {
                "queued": True,
                "processing": True,
                "message": f"Task already {task.status.value}"
            }

        if task.status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
            return {
                "queued": False,
                "processing": False,
                "message": f"Task already {task.status.value}"
            }

        # Submit to Celery for processing immediately
        max_attempts = max(1, settings.QUEUE_ENQUEUE_MAX_RETRIES + 1)
        base_delay = max(0.0, settings.QUEUE_ENQUEUE_BASE_DELAY)
        max_delay = max(base_delay, settings.QUEUE_ENQUEUE_MAX_DELAY)

        celery_task = None
        last_error = None
        for attempt in range(1, max_attempts + 1):
            if not _broker_reachable(settings.celery_broker_url):
                last_error = "broker unreachable"
            else:
                try:
                    celery_task = process_task.delay(task.id)
                    break
                except Exception as exc:
                    last_error = str(exc)

            if attempt < max_attempts:
                delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                jitter = random.uniform(0.0, min(0.5, delay * 0.1))
                time.sleep(delay + jitter)

        if celery_task is None:
            return {
                "queued": False,
                "processing": False,
                "message": f"Queue unavailable after {max_attempts} attempts: {last_error}"
            }

        # Set task to queued status
        task.status = TaskStatus.QUEUED
        self.db.commit()

        # Increment queue count
        self.agent_status_service.increment_queue(
            user_id=task.user_id,
            agent_type=task.agent_type
        )

        # Add history entry
        history = TaskHistory(
            task_id=task.id,
            status=TaskStatus.QUEUED,
            message="Task queued for processing",
            event_metadata={"action_type": "task_assigned"}
        )
        self.db.add(history)
        self.db.commit()

        # Broadcast task status change
        self._broadcast_task_status(
            user_id=task.user_id,
            task_id=task.task_id,
            agent_type=task.agent_type,
            status=TaskStatus.QUEUED.value,
            message="Task queued for processing"
        )

        return {
            "queued": True,
            "processing": True,
            "celery_task_id": celery_task.id,
            "message": "Task submitted for processing"
        }
    
    def get_queue_status(self, user_id: int, agent_type: str) -> Dict[str, Any]:
        """
        Get the current queue status for an agent.
        
        Args:
            user_id: User ID
            agent_type: Agent type
            
        Returns:
            Dictionary with queue status
        """
        # Get agent status
        agent_status = self.agent_status_service.get_status(user_id, agent_type)
        
        # Get pending and queued tasks
        pending_tasks = self.task_service.get_pending_tasks(
            user_id=user_id,
            agent_type=agent_type
        )
        
        queued_tasks = self.task_service.get_tasks(
            user_id=user_id,
            agent_type=agent_type,
            status=TaskStatus.QUEUED
        )[0]
        
        in_progress_tasks = self.task_service.get_tasks(
            user_id=user_id,
            agent_type=agent_type,
            status=TaskStatus.IN_PROGRESS
        )[0]
        
        return {
            "agent_type": agent_type,
            "agent_status": agent_status.status.value if agent_status else "available",
            "current_task_id": agent_status.current_task_id if agent_status else None,
            "tasks_in_queue": len(pending_tasks) + len(queued_tasks),
            "pending_tasks": len(pending_tasks),
            "queued_tasks": len(queued_tasks),
            "in_progress_tasks": len(in_progress_tasks),
            "queue": [
                {
                    "task_id": t.task_id,
                    "title": t.title,
                    "priority": t.priority.value,
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat()
                }
                for t in (pending_tasks + queued_tasks)
            ]
        }
    
    def cancel_task(self, task_id: int, user_id: int) -> Dict[str, Any]:
        """
        Cancel a task in the queue.
        
        Args:
            task_id: Database ID of the task
            user_id: User ID (for authorization)
            
        Returns:
            Dictionary with cancellation status
        """
        task = self.task_service.get_task_by_id(task_id, user_id)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Can only cancel pending or queued tasks
        if task.status not in [TaskStatus.PENDING, TaskStatus.QUEUED]:
            return {
                "success": False,
                "message": f"Cannot cancel task with status {task.status.value}"
            }
        
        # Update status to cancelled
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        self.db.commit()
        
        # Decrement queue count if it was queued
        if task.status == TaskStatus.QUEUED:
            self.agent_status_service.decrement_queue(
                user_id=task.user_id,
                agent_type=task.agent_type
            )
        
        # Add history entry
        history = TaskHistory(
            task_id=task.id,
            status=TaskStatus.CANCELLED,
            message="Task cancelled by user",
            event_metadata={"action_type": "task_cancelled"}
        )
        self.db.add(history)
        self.db.commit()
        
        return {
            "success": True,
            "message": "Task cancelled successfully"
        }
    
    def _broadcast_queue_update(
        self,
        user_id: int,
        agent_type: str,
        tasks_in_queue: int,
        queue_position: Optional[int] = None
    ):
        """Broadcast queue update via WebSocket."""
        try:
            # Try to get the running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the coroutine
                asyncio.create_task(
                    connection_manager.broadcast_queue_update(
                        user_id=user_id,
                        agent_type=agent_type,
                        tasks_in_queue=tasks_in_queue,
                        queue_position=queue_position
                    )
                )
            except RuntimeError:
                # No running loop, we're in sync context - skip broadcast
                # WebSocket broadcasts will be handled by the Celery worker
                pass
        except Exception:
            # Silently fail on broadcast errors
            pass
    
    def _broadcast_task_status(
        self,
        user_id: int,
        task_id: str,
        agent_type: str,
        status: str,
        message: Optional[str] = None
    ):
        """Broadcast task status change via WebSocket."""
        try:
            # Try to get the running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the coroutine
                asyncio.create_task(
                    connection_manager.broadcast_task_status_change(
                        user_id=user_id,
                        task_id=task_id,
                        agent_type=agent_type,
                        status=status,
                        message_text=message
                    )
                )
            except RuntimeError:
                # No running loop, we're in sync context - skip broadcast
                # WebSocket broadcasts will be handled by the Celery worker
                pass
        except Exception:
            # Silently fail on broadcast errors
            pass


# Celery task definition
@celery_app.task(
    bind=True,
    name="app.workers.background_worker.process_task",
    max_retries=settings.TASK_MAX_RETRIES,
    default_retry_delay=settings.TASK_RETRY_DELAY
)
def process_task(self: Task, task_id: int) -> Dict[str, Any]:
    """
    Celery task to process a background task.
    
    Args:
        task_id: Database ID of the task to process
        
    Returns:
        Dictionary with processing results
    """
    db = SessionLocal()
    
    try:
        processor = TaskProcessor(db)
        result = processor.process_task(task_id)
        return result
        
    except Exception as e:
        # Log error
        error_message = str(e)
        error_trace = traceback.format_exc()
        
        # Retry if not max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        # Max retries reached, mark as failed
        return {
            "success": False,
            "task_id": task_id,
            "error": error_message,
            "trace": error_trace,
            "max_retries_reached": True
        }
        
    finally:
        db.close()


# Helper function to enqueue a task
def enqueue_task(task_id: int) -> Dict[str, Any]:
    """
    Helper function to enqueue a task for processing.
    
    Args:
        task_id: Database ID of the task to enqueue
        
    Returns:
        Dictionary with queue status
    """
    db = SessionLocal()
    
    try:
        queue_manager = AgentQueueManager(db)
        return queue_manager.enqueue_task(task_id)
        
    finally:
        db.close()


# Helper function to get queue status
def get_queue_status(user_id: int, agent_type: str) -> Dict[str, Any]:
    """
    Helper function to get queue status for an agent.
    
    Args:
        user_id: User ID
        agent_type: Agent type
        
    Returns:
        Dictionary with queue status
    """
    db = SessionLocal()
    
    try:
        queue_manager = AgentQueueManager(db)
        return queue_manager.get_queue_status(user_id, agent_type)
        
    finally:
        db.close()


# Helper function to cancel a task
def cancel_task(task_id: int, user_id: int) -> Dict[str, Any]:
    """
    Helper function to cancel a task.
    
    Args:
        task_id: Database ID of the task
        user_id: User ID (for authorization)
        
    Returns:
        Dictionary with cancellation status
    """
    db = SessionLocal()
    
    try:
        queue_manager = AgentQueueManager(db)
        return queue_manager.cancel_task(task_id, user_id)
        
    finally:
        db.close()

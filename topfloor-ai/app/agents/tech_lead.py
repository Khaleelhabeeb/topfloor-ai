"""
Team Lead Agent - Project manager that assigns tasks and tracks progress
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from google.adk.tools import FunctionTool

from app.agents.base import BaseAgent
from app.agents.registry import AgentDefinition
from app.services.task_service import TaskService
from app.services.agent_status_service import AgentStatusService
from app.schemas.task import TaskCreate
from app.models.task import TaskType, TaskPriority, TaskStatus


class TeamLeadAgent(BaseAgent):
    """
    Project manager that assigns tasks to other agents,
    tracks progress, and coordinates team workflows.
    """
    
    def __init__(
        self,
        definition: AgentDefinition,
        user_context: Optional[Dict[str, Any]] = None,
        task_service: Optional[TaskService] = None,
        agent_status_service: Optional[AgentStatusService] = None
    ):
        """
        Initialize Team Lead agent with services.
        
        Args:
            definition: Agent definition from registry
            user_context: Optional user-specific context
            task_service: Task service for task management
            agent_status_service: Agent status service for status tracking
        """
        super().__init__(definition, user_context)
        self._task_service = task_service
        self._agent_status_service = agent_status_service
    
    def build_tools(self) -> List[FunctionTool]:
        """
        Build task management tools for the team lead.
        
        Returns:
            List of task management tools
        """
        tools = []
        
        # Get user_id from context
        user_id = self.user_context.get("user_id") if self.user_context else None
        
        # Task assignment tool
        @FunctionTool
        def assign_task(
            agent_type: str,
            title: str,
            description: str,
            priority: str = "medium",
            task_type: str = "background"
        ) -> Dict[str, Any]:
            """
            Assign a task to a specific agent.
            
            Args:
                agent_type: Type of agent to assign task to (finance, data_analyst, researcher, devops)
                title: Short title for the task
                description: Clear description of the task
                priority: Task priority (low, medium, high, critical)
                task_type: Type of task (chat, background)
                
            Returns:
                Task assignment confirmation with task_id
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "assigned_to": agent_type,
                    "task": description,
                    "priority": priority,
                    "status": "failed"
                }
            
            try:
                # Map priority string to enum
                priority_map = {
                    "low": TaskPriority.LOW,
                    "medium": TaskPriority.MEDIUM,
                    "high": TaskPriority.HIGH,
                    "critical": TaskPriority.CRITICAL
                }
                priority_enum = priority_map.get(priority.lower(), TaskPriority.MEDIUM)
                
                # Map task type string to enum
                task_type_map = {
                    "chat": TaskType.CHAT,
                    "background": TaskType.BACKGROUND
                }
                task_type_enum = task_type_map.get(task_type.lower(), TaskType.BACKGROUND)
                
                # Create task
                task_data = TaskCreate(
                    agent_type=agent_type,
                    title=title,
                    description=description,
                    task_type=task_type_enum,
                    priority=priority_enum,
                    input_data={}
                )
                
                task = self._task_service.create_task(user_id, task_data)

                queue_message = None
                if task.task_type == TaskType.BACKGROUND:
                    try:
                        from app.workers.background_worker import enqueue_task
                        queue_result = enqueue_task(task.id)
                        if not queue_result.get("queued", True):
                            queue_message = queue_result.get("message")
                    except Exception as exc:
                        queue_message = str(exc)
                
                return {
                    "task_id": task.task_id,
                    "assigned_to": agent_type,
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "task_type": task_type,
                    "status": task.status.value,
                    "queue_message": queue_message,
                    "created_at": task.created_at.isoformat()
                }
            except Exception as e:
                return {
                    "error": f"Failed to assign task: {str(e)}",
                    "assigned_to": agent_type,
                    "task": description,
                    "priority": priority,
                    "status": "failed"
                }
        
        # Get agent status tool
        @FunctionTool
        def get_agent_status(agent_type: str) -> Dict[str, Any]:
            """
            Get current status and workload of an agent.
            
            Args:
                agent_type: Type of agent to check (finance, data_analyst, researcher, devops)
                
            Returns:
                Agent status information including availability and queue length
            """
            if not self._agent_status_service or not user_id:
                return {
                    "agent_type": agent_type,
                    "status": "unknown",
                    "error": "Agent status service not available or user not authenticated"
                }
            
            try:
                status = self._agent_status_service.get_or_create_status(user_id, agent_type)
                
                # Get task counts if task service is available
                task_counts = {}
                if self._task_service:
                    task_counts = self._task_service.count_tasks_by_status(user_id, agent_type)
                
                return {
                    "agent_type": agent_type,
                    "status": status.status.value,
                    "current_task_id": status.current_task_id,
                    "tasks_in_queue": status.tasks_in_queue,
                    "last_active_at": status.last_active_at.isoformat() if status.last_active_at else None,
                    "task_counts": task_counts
                }
            except Exception as e:
                return {
                    "agent_type": agent_type,
                    "status": "error",
                    "error": f"Failed to get agent status: {str(e)}"
                }
        
        # List pending tasks tool
        @FunctionTool
        def list_pending_tasks(agent_type: Optional[str] = None) -> Dict[str, Any]:
            """
            List all pending tasks across the team or for a specific agent.
            
            Args:
                agent_type: Optional agent type to filter by (finance, data_analyst, researcher, devops)
                
            Returns:
                List of pending tasks with details
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "tasks": []
                }
            
            try:
                pending_tasks = self._task_service.get_pending_tasks(user_id, agent_type)
                
                tasks_list = []
                for task in pending_tasks:
                    tasks_list.append({
                        "task_id": task.task_id,
                        "agent_type": task.agent_type,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority.value,
                        "task_type": task.task_type.value,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat()
                    })
                
                return {
                    "total_pending": len(tasks_list),
                    "agent_filter": agent_type,
                    "tasks": tasks_list
                }
            except Exception as e:
                return {
                    "error": f"Failed to list pending tasks: {str(e)}",
                    "tasks": []
                }
        
        # Update task status tool
        @FunctionTool
        def update_task_status(
            task_id: str,
            status: str,
            error_message: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Update the status of a task.
            
            Args:
                task_id: ID of the task to update
                status: New status (pending, queued, in_progress, completed, failed, cancelled)
                error_message: Optional error message if status is failed
                
            Returns:
                Updated task information
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "task_id": task_id,
                    "status": status,
                    "updated": False
                }
            
            try:
                # Get task by task_id string
                task = self._task_service.get_task_by_task_id(task_id, user_id)
                
                if not task:
                    return {
                        "error": f"Task not found: {task_id}",
                        "task_id": task_id,
                        "status": status,
                        "updated": False
                    }
                
                # Map status string to enum
                status_map = {
                    "pending": TaskStatus.PENDING,
                    "queued": TaskStatus.QUEUED,
                    "in_progress": TaskStatus.IN_PROGRESS,
                    "completed": TaskStatus.COMPLETED,
                    "failed": TaskStatus.FAILED,
                    "cancelled": TaskStatus.CANCELLED
                }
                status_enum = status_map.get(status.lower())
                
                if not status_enum:
                    return {
                        "error": f"Invalid status: {status}",
                        "task_id": task_id,
                        "status": status,
                        "updated": False
                    }
                
                # Update task status
                updated_task = self._task_service.update_task_status(
                    task.id,
                    user_id,
                    status_enum,
                    error_message
                )
                
                if not updated_task:
                    return {
                        "error": "Failed to update task",
                        "task_id": task_id,
                        "status": status,
                        "updated": False
                    }
                
                return {
                    "task_id": updated_task.task_id,
                    "agent_type": updated_task.agent_type,
                    "title": updated_task.title,
                    "status": updated_task.status.value,
                    "updated_at": updated_task.updated_at.isoformat(),
                    "updated": True
                }
            except Exception as e:
                return {
                    "error": f"Failed to update task status: {str(e)}",
                    "task_id": task_id,
                    "status": status,
                    "updated": False
                }
        
        # Get all agents status tool
        @FunctionTool
        def get_all_agents_status() -> Dict[str, Any]:
            """
            Get status of all agents in the team.
            
            Returns:
                Summary of all agent statuses and workloads
            """
            if not self._agent_status_service or not user_id:
                return {
                    "error": "Agent status service not available or user not authenticated",
                    "agents": []
                }
            
            try:
                summary = self._agent_status_service.get_status_summary(user_id)
                return summary
            except Exception as e:
                return {
                    "error": f"Failed to get team status: {str(e)}",
                    "agents": []
                }
        
        # Get task details tool
        @FunctionTool
        def get_task_details(task_id: str) -> Dict[str, Any]:
            """
            Get detailed information about a specific task.
            
            Args:
                task_id: ID of the task to retrieve
                
            Returns:
                Detailed task information
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "task_id": task_id
                }
            
            try:
                task = self._task_service.get_task_by_task_id(task_id, user_id)
                
                if not task:
                    return {
                        "error": f"Task not found: {task_id}",
                        "task_id": task_id
                    }
                
                return {
                    "task_id": task.task_id,
                    "agent_type": task.agent_type,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "input_data": task.input_data,
                    "result_data": task.result_data,
                    "error_message": task.error_message,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
            except Exception as e:
                return {
                    "error": f"Failed to get task details: {str(e)}",
                    "task_id": task_id
                }
        
        # Get task status tool
        @FunctionTool
        def get_task_status(task_id: str) -> Dict[str, Any]:
            """
            Get the current status of a specific task.
            
            Args:
                task_id: ID of the task to check
                
            Returns:
                Task status information including progress and timing
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "task_id": task_id
                }
            
            try:
                task = self._task_service.get_task_by_task_id(task_id, user_id)
                
                if not task:
                    return {
                        "error": f"Task not found: {task_id}",
                        "task_id": task_id
                    }
                
                # Calculate duration if task has started
                duration = None
                if task.started_at:
                    end_time = task.completed_at if task.completed_at else datetime.now()
                    duration = (end_time - task.started_at).total_seconds()
                
                return {
                    "task_id": task.task_id,
                    "agent_type": task.agent_type,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "duration_seconds": duration,
                    "has_error": task.error_message is not None,
                    "error_message": task.error_message
                }
            except Exception as e:
                return {
                    "error": f"Failed to get task status: {str(e)}",
                    "task_id": task_id
                }
        
        # Get completed tasks tool
        @FunctionTool
        def get_completed_tasks(
            agent_type: Optional[str] = None,
            limit: int = 10
        ) -> Dict[str, Any]:
            """
            Get recently completed tasks across the team or for a specific agent.
            
            Args:
                agent_type: Optional agent type to filter by (finance, data_analyst, researcher, devops)
                limit: Maximum number of tasks to return (default: 10)
                
            Returns:
                List of completed tasks with results
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "tasks": []
                }
            
            try:
                tasks, total = self._task_service.get_tasks(
                    user_id=user_id,
                    agent_type=agent_type,
                    status=TaskStatus.COMPLETED,
                    sort_by="completed_at",
                    sort_order="desc",
                    limit=limit
                )
                
                tasks_list = []
                for task in tasks:
                    duration = None
                    if task.started_at and task.completed_at:
                        duration = (task.completed_at - task.started_at).total_seconds()
                    
                    tasks_list.append({
                        "task_id": task.task_id,
                        "agent_type": task.agent_type,
                        "title": task.title,
                        "priority": task.priority.value,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "duration_seconds": duration,
                        "has_result": task.result_data is not None
                    })
                
                return {
                    "total_completed": total,
                    "returned": len(tasks_list),
                    "agent_filter": agent_type,
                    "tasks": tasks_list
                }
            except Exception as e:
                return {
                    "error": f"Failed to get completed tasks: {str(e)}",
                    "tasks": []
                }
        
        # Get failed tasks tool
        @FunctionTool
        def get_failed_tasks(
            agent_type: Optional[str] = None,
            limit: int = 10
        ) -> Dict[str, Any]:
            """
            Get recently failed tasks with error details.
            
            Args:
                agent_type: Optional agent type to filter by (finance, data_analyst, researcher, devops)
                limit: Maximum number of tasks to return (default: 10)
                
            Returns:
                List of failed tasks with error messages
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "tasks": []
                }
            
            try:
                tasks, total = self._task_service.get_tasks(
                    user_id=user_id,
                    agent_type=agent_type,
                    status=TaskStatus.FAILED,
                    sort_by="updated_at",
                    sort_order="desc",
                    limit=limit
                )
                
                tasks_list = []
                for task in tasks:
                    tasks_list.append({
                        "task_id": task.task_id,
                        "agent_type": task.agent_type,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority.value,
                        "error_message": task.error_message,
                        "failed_at": task.updated_at.isoformat(),
                        "created_at": task.created_at.isoformat()
                    })
                
                return {
                    "total_failed": total,
                    "returned": len(tasks_list),
                    "agent_filter": agent_type,
                    "tasks": tasks_list
                }
            except Exception as e:
                return {
                    "error": f"Failed to get failed tasks: {str(e)}",
                    "tasks": []
                }
        
        # Get in-progress tasks tool
        @FunctionTool
        def get_in_progress_tasks(
            agent_type: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get all currently in-progress tasks across the team or for a specific agent.
            
            Args:
                agent_type: Optional agent type to filter by (finance, data_analyst, researcher, devops)
                
            Returns:
                List of in-progress tasks with timing information
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "tasks": []
                }
            
            try:
                tasks, total = self._task_service.get_tasks(
                    user_id=user_id,
                    agent_type=agent_type,
                    status=TaskStatus.IN_PROGRESS,
                    sort_by="started_at",
                    sort_order="asc"
                )
                
                tasks_list = []
                for task in tasks:
                    duration = None
                    if task.started_at:
                        duration = (datetime.now() - task.started_at).total_seconds()
                    
                    tasks_list.append({
                        "task_id": task.task_id,
                        "agent_type": task.agent_type,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority.value,
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "duration_seconds": duration
                    })
                
                return {
                    "total_in_progress": total,
                    "agent_filter": agent_type,
                    "tasks": tasks_list
                }
            except Exception as e:
                return {
                    "error": f"Failed to get in-progress tasks: {str(e)}",
                    "tasks": []
                }
        
        # Get task statistics tool
        @FunctionTool
        def get_task_statistics(
            agent_type: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get comprehensive task statistics for the team or a specific agent.
            
            Args:
                agent_type: Optional agent type to filter by (finance, data_analyst, researcher, devops)
                
            Returns:
                Task statistics including counts by status, priority, and type
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated"
                }
            
            try:
                # Get task counts by status
                status_counts = self._task_service.count_tasks_by_status(user_id, agent_type)
                
                # Get all tasks for additional statistics
                all_tasks, total = self._task_service.get_tasks(
                    user_id=user_id,
                    agent_type=agent_type,
                    limit=1000  # Get a large sample
                )
                
                # Count by priority
                priority_counts = {
                    "low": 0,
                    "medium": 0,
                    "high": 0,
                    "critical": 0
                }
                
                # Count by type
                type_counts = {
                    "chat": 0,
                    "background": 0
                }
                
                # Calculate average completion time
                completion_times = []
                
                for task in all_tasks:
                    # Count by priority
                    priority_counts[task.priority.value] += 1
                    
                    # Count by type
                    type_counts[task.task_type.value] += 1
                    
                    # Track completion times
                    if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at:
                        duration = (task.completed_at - task.started_at).total_seconds()
                        completion_times.append(duration)
                
                avg_completion_time = None
                if completion_times:
                    avg_completion_time = sum(completion_times) / len(completion_times)
                
                return {
                    "agent_filter": agent_type,
                    "total_tasks": total,
                    "status_counts": status_counts,
                    "priority_counts": priority_counts,
                    "type_counts": type_counts,
                    "average_completion_time_seconds": avg_completion_time,
                    "completed_tasks_count": len(completion_times)
                }
            except Exception as e:
                return {
                    "error": f"Failed to get task statistics: {str(e)}"
                }
        
        # Generate comprehensive status report tool
        @FunctionTool
        def generate_status_report(
            include_agents: bool = True,
            include_tasks: bool = True,
            include_statistics: bool = True,
            agent_type: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Generate a comprehensive status report for the team or a specific agent.
            
            Args:
                include_agents: Include agent status information (default: True)
                include_tasks: Include task breakdown by status (default: True)
                include_statistics: Include task statistics and metrics (default: True)
                agent_type: Optional agent type to filter by (finance, data_analyst, researcher, devops)
                
            Returns:
                Comprehensive status report with agent statuses, task breakdowns, and statistics
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Services not available or user not authenticated",
                    "report_generated": False
                }
            
            try:
                report = {
                    "report_type": "status_report",
                    "generated_at": datetime.now().isoformat(),
                    "scope": agent_type if agent_type else "all_agents"
                }
                
                # Include agent status information
                if include_agents and self._agent_status_service:
                    if agent_type:
                        status = self._agent_status_service.get_or_create_status(user_id, agent_type)
                        report["agent_status"] = {
                            "agent_type": agent_type,
                            "status": status.status.value,
                            "current_task_id": status.current_task_id,
                            "tasks_in_queue": status.tasks_in_queue,
                            "last_active_at": status.last_active_at.isoformat() if status.last_active_at else None
                        }
                    else:
                        summary = self._agent_status_service.get_status_summary(user_id)
                        report["agents_status"] = summary
                
                # Include task breakdown
                if include_tasks:
                    status_counts = self._task_service.count_tasks_by_status(user_id, agent_type)
                    report["task_breakdown"] = status_counts
                    
                    # Get pending tasks
                    pending_tasks = self._task_service.get_pending_tasks(user_id, agent_type)
                    report["pending_tasks_count"] = len(pending_tasks)
                    
                    # Get in-progress tasks
                    in_progress_tasks, _ = self._task_service.get_tasks(
                        user_id=user_id,
                        agent_type=agent_type,
                        status=TaskStatus.IN_PROGRESS
                    )
                    report["in_progress_tasks_count"] = len(in_progress_tasks)
                    
                    # Get recently completed tasks
                    completed_tasks, _ = self._task_service.get_tasks(
                        user_id=user_id,
                        agent_type=agent_type,
                        status=TaskStatus.COMPLETED,
                        limit=10
                    )
                    report["recent_completed_count"] = len(completed_tasks)
                
                # Include statistics
                if include_statistics:
                    # Get task counts by status
                    status_counts = self._task_service.count_tasks_by_status(user_id, agent_type)
                    
                    # Get all tasks for statistics
                    all_tasks, total = self._task_service.get_tasks(
                        user_id=user_id,
                        agent_type=agent_type,
                        limit=1000
                    )
                    
                    # Calculate metrics
                    priority_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
                    completion_times = []
                    
                    for task in all_tasks:
                        priority_counts[task.priority.value] += 1
                        if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at:
                            duration = (task.completed_at - task.started_at).total_seconds()
                            completion_times.append(duration)
                    
                    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else None
                    
                    report["statistics"] = {
                        "total_tasks": total,
                        "priority_distribution": priority_counts,
                        "average_completion_time_seconds": avg_completion_time,
                        "completed_tasks_analyzed": len(completion_times)
                    }
                
                report["report_generated"] = True
                return report
                
            except Exception as e:
                return {
                    "error": f"Failed to generate status report: {str(e)}",
                    "report_generated": False
                }
        
        # Generate progress report tool
        @FunctionTool
        def generate_progress_report(
            agent_type: Optional[str] = None,
            time_period_hours: int = 24,
            include_details: bool = False
        ) -> Dict[str, Any]:
            """
            Generate a progress report showing completed, in-progress, and pending tasks.
            
            Args:
                agent_type: Optional agent type to filter by (finance, data_analyst, researcher, devops)
                time_period_hours: Time period to analyze in hours (default: 24)
                include_details: Include detailed task information (default: False)
                
            Returns:
                Progress report with task progress, completion rates, and issues
            """
            if not self._task_service or not user_id:
                return {
                    "error": "Task service not available or user not authenticated",
                    "report_generated": False
                }
            
            try:
                from datetime import timedelta
                
                report = {
                    "report_type": "progress_report",
                    "generated_at": datetime.now().isoformat(),
                    "scope": agent_type if agent_type else "all_agents",
                    "time_period_hours": time_period_hours
                }
                
                # Calculate time threshold
                time_threshold = datetime.now() - timedelta(hours=time_period_hours)
                
                # Get all tasks
                all_tasks, total = self._task_service.get_tasks(
                    user_id=user_id,
                    agent_type=agent_type,
                    limit=1000
                )
                
                # Categorize tasks
                completed_tasks = []
                in_progress_tasks = []
                pending_tasks = []
                failed_tasks = []
                
                for task in all_tasks:
                    if task.status == TaskStatus.COMPLETED:
                        # Only include if completed within time period
                        if task.completed_at and task.completed_at >= time_threshold:
                            completed_tasks.append(task)
                    elif task.status == TaskStatus.IN_PROGRESS:
                        in_progress_tasks.append(task)
                    elif task.status in [TaskStatus.PENDING, TaskStatus.QUEUED]:
                        pending_tasks.append(task)
                    elif task.status == TaskStatus.FAILED:
                        # Only include if failed within time period
                        if task.updated_at >= time_threshold:
                            failed_tasks.append(task)
                
                # Build report sections
                report["completed"] = {
                    "count": len(completed_tasks),
                    "tasks": []
                }
                
                report["in_progress"] = {
                    "count": len(in_progress_tasks),
                    "tasks": []
                }
                
                report["pending"] = {
                    "count": len(pending_tasks),
                    "tasks": []
                }
                
                report["failed"] = {
                    "count": len(failed_tasks),
                    "tasks": []
                }
                
                # Add task details if requested
                if include_details:
                    for task in completed_tasks:
                        duration = None
                        if task.started_at and task.completed_at:
                            duration = (task.completed_at - task.started_at).total_seconds()
                        
                        report["completed"]["tasks"].append({
                            "task_id": task.task_id,
                            "agent_type": task.agent_type,
                            "title": task.title,
                            "priority": task.priority.value,
                            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                            "duration_seconds": duration
                        })
                    
                    for task in in_progress_tasks:
                        duration = None
                        if task.started_at:
                            duration = (datetime.now() - task.started_at).total_seconds()
                        
                        report["in_progress"]["tasks"].append({
                            "task_id": task.task_id,
                            "agent_type": task.agent_type,
                            "title": task.title,
                            "priority": task.priority.value,
                            "started_at": task.started_at.isoformat() if task.started_at else None,
                            "duration_seconds": duration
                        })
                    
                    for task in pending_tasks:
                        report["pending"]["tasks"].append({
                            "task_id": task.task_id,
                            "agent_type": task.agent_type,
                            "title": task.title,
                            "priority": task.priority.value,
                            "created_at": task.created_at.isoformat()
                        })
                    
                    for task in failed_tasks:
                        report["failed"]["tasks"].append({
                            "task_id": task.task_id,
                            "agent_type": task.agent_type,
                            "title": task.title,
                            "priority": task.priority.value,
                            "error_message": task.error_message,
                            "failed_at": task.updated_at.isoformat()
                        })
                
                # Identify issues and blockers
                issues = []
                
                # Check for failed tasks
                if len(failed_tasks) > 0:
                    issues.append({
                        "type": "failed_tasks",
                        "severity": "high",
                        "message": f"{len(failed_tasks)} task(s) failed in the last {time_period_hours} hours",
                        "count": len(failed_tasks)
                    })
                
                # Check for long-running tasks
                long_running_threshold = 3600  # 1 hour in seconds
                long_running_tasks = []
                for task in in_progress_tasks:
                    if task.started_at:
                        duration = (datetime.now() - task.started_at).total_seconds()
                        if duration > long_running_threshold:
                            long_running_tasks.append(task)
                
                if long_running_tasks:
                    issues.append({
                        "type": "long_running_tasks",
                        "severity": "medium",
                        "message": f"{len(long_running_tasks)} task(s) running longer than 1 hour",
                        "count": len(long_running_tasks)
                    })
                
                # Check for high priority pending tasks
                high_priority_pending = [t for t in pending_tasks if t.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]]
                if high_priority_pending:
                    issues.append({
                        "type": "high_priority_pending",
                        "severity": "medium",
                        "message": f"{len(high_priority_pending)} high/critical priority task(s) pending",
                        "count": len(high_priority_pending)
                    })
                
                report["issues"] = issues
                report["has_issues"] = len(issues) > 0
                
                # Calculate completion rate
                total_actionable = len(completed_tasks) + len(failed_tasks)
                completion_rate = (len(completed_tasks) / total_actionable * 100) if total_actionable > 0 else 0
                
                report["metrics"] = {
                    "completion_rate_percent": round(completion_rate, 2),
                    "total_completed": len(completed_tasks),
                    "total_failed": len(failed_tasks),
                    "total_in_progress": len(in_progress_tasks),
                    "total_pending": len(pending_tasks)
                }
                
                report["report_generated"] = True
                return report
                
            except Exception as e:
                return {
                    "error": f"Failed to generate progress report: {str(e)}",
                    "report_generated": False
                }
        
        # Generate team summary report tool
        @FunctionTool
        def generate_team_summary() -> Dict[str, Any]:
            """
            Generate a high-level summary of the entire team's status and performance.
            
            Returns:
                Team summary with agent statuses, workload distribution, and key metrics
            """
            if not self._task_service or not self._agent_status_service or not user_id:
                return {
                    "error": "Services not available or user not authenticated",
                    "report_generated": False
                }
            
            try:
                report = {
                    "report_type": "team_summary",
                    "generated_at": datetime.now().isoformat()
                }
                
                # Get all agents status
                agents_summary = self._agent_status_service.get_status_summary(user_id)
                report["team_status"] = agents_summary
                
                # Get task distribution by agent
                agent_types = ["finance", "data_analyst", "researcher", "devops"]
                workload_distribution = {}
                
                for agent_type in agent_types:
                    status_counts = self._task_service.count_tasks_by_status(user_id, agent_type)
                    workload_distribution[agent_type] = {
                        "total_tasks": sum(status_counts.values()),
                        "pending": status_counts.get("pending", 0) + status_counts.get("queued", 0),
                        "in_progress": status_counts.get("in_progress", 0),
                        "completed": status_counts.get("completed", 0),
                        "failed": status_counts.get("failed", 0)
                    }
                
                report["workload_distribution"] = workload_distribution
                
                # Calculate team-wide metrics
                all_tasks, total = self._task_service.get_tasks(user_id=user_id, limit=1000)
                
                total_completed = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
                total_failed = sum(1 for t in all_tasks if t.status == TaskStatus.FAILED)
                total_in_progress = sum(1 for t in all_tasks if t.status == TaskStatus.IN_PROGRESS)
                total_pending = sum(1 for t in all_tasks if t.status in [TaskStatus.PENDING, TaskStatus.QUEUED])
                
                # Calculate average completion time
                completion_times = []
                for task in all_tasks:
                    if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at:
                        duration = (task.completed_at - task.started_at).total_seconds()
                        completion_times.append(duration)
                
                avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else None
                
                report["team_metrics"] = {
                    "total_tasks": total,
                    "completed": total_completed,
                    "failed": total_failed,
                    "in_progress": total_in_progress,
                    "pending": total_pending,
                    "average_completion_time_seconds": avg_completion_time,
                    "success_rate_percent": round((total_completed / (total_completed + total_failed) * 100), 2) if (total_completed + total_failed) > 0 else 0
                }
                
                # Identify team-wide issues
                issues = []
                
                # Check for overloaded agents
                for agent_type, workload in workload_distribution.items():
                    if workload["pending"] > 10:
                        issues.append({
                            "type": "high_workload",
                            "agent": agent_type,
                            "severity": "medium",
                            "message": f"{agent_type} has {workload['pending']} pending tasks"
                        })
                
                # Check for failed tasks
                if total_failed > 0:
                    issues.append({
                        "type": "failed_tasks",
                        "severity": "high",
                        "message": f"{total_failed} task(s) have failed",
                        "count": total_failed
                    })
                
                report["issues"] = issues
                report["has_issues"] = len(issues) > 0
                report["report_generated"] = True
                
                return report
                
            except Exception as e:
                return {
                    "error": f"Failed to generate team summary: {str(e)}",
                    "report_generated": False
                }
        
        tools.extend([
            assign_task,
            get_agent_status,
            list_pending_tasks,
            update_task_status,
            get_all_agents_status,
            get_task_details,
            get_task_status,
            get_completed_tasks,
            get_failed_tasks,
            get_in_progress_tasks,
            get_task_statistics,
            generate_status_report,
            generate_progress_report,
            generate_team_summary
        ])
        
        return tools

"""
Team Lead Agent - Project manager that assigns tasks and tracks progress
"""

from typing import List, Dict, Any, Optional
from google.adk.tools import FunctionTool

from app.agents.base import BaseAgent
from app.agents.registry import AgentDefinition


class TeamLeadAgent(BaseAgent):
    """
    Project manager that assigns tasks to other agents,
    tracks progress, and coordinates team workflows.
    """
    
    def build_tools(self) -> List[FunctionTool]:
        """
        Build task management tools for the team lead.
        
        Returns:
            List of task management tools
        """
        tools = []
        
        # Task assignment tool
        @FunctionTool
        def assign_task(
            agent_name: str,
            task_description: str,
            priority: str = "medium",
            deadline: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Assign a task to a specific agent.
            
            Args:
                agent_name: Name of the agent to assign task to (researcher, developer, data_analyst)
                task_description: Clear description of the task
                priority: Task priority (low, medium, high, critical)
                deadline: Optional deadline for the task
                
            Returns:
                Task assignment confirmation with task_id
            """
            # TODO: Integrate with task service in STEP 3
            import uuid
            task_id = str(uuid.uuid4())[:8]
            
            return {
                "task_id": task_id,
                "assigned_to": agent_name,
                "task": task_description,
                "priority": priority,
                "deadline": deadline,
                "status": "assigned"
            }
        
        # Get agent status tool
        @FunctionTool
        def get_agent_status(agent_name: str) -> Dict[str, Any]:
            """
            Get current status and workload of an agent.
            
            Args:
                agent_name: Name of the agent to check
                
            Returns:
                Agent status information
            """
            # TODO: Integrate with session service in STEP 4
            return {
                "agent_name": agent_name,
                "status": "available",
                "active_tasks": 0,
                "completed_tasks": 0
            }
        
        # List pending tasks tool
        @FunctionTool
        def list_pending_tasks() -> List[Dict[str, Any]]:
            """
            List all pending tasks across the team.
            
            Returns:
                List of pending tasks
            """
            # TODO: Integrate with task service in STEP 3
            return []
        
        # Update task status tool
        @FunctionTool
        def update_task_status(
            task_id: str,
            status: str,
            result: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Update the status of a task.
            
            Args:
                task_id: ID of the task to update
                status: New status (in_progress, completed, blocked, cancelled)
                result: Optional result data for completed tasks
                
            Returns:
                Updated task information
            """
            # TODO: Integrate with task service in STEP 3
            return {
                "task_id": task_id,
                "status": status,
                "result": result,
                "updated": True
            }
        
        tools.extend([
            assign_task,
            get_agent_status,
            list_pending_tasks,
            update_task_status
        ])
        
        return tools

"""
WebSocket Service - Manages WebSocket connections and broadcasts
Handles real-time agent status updates and notifications
"""

from fastapi import WebSocket
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timezone
import json
import asyncio
from collections import defaultdict


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages to connected clients.
    Supports user-specific and agent-specific broadcasting.
    """
    
    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = defaultdict(dict)
        
        # Agent subscriptions: {user_id: {agent_type: set(connection_ids)}}
        self.agent_subscriptions: Dict[int, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        
        # Connection metadata: {connection_id: {user_id, agent_type, connected_at}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: int,
        connection_id: str,
        agent_type: Optional[str] = None
    ):
        """
        Register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
            connection_id: Unique connection identifier
            agent_type: Optional agent type to subscribe to
        """
        await websocket.accept()
        
        # Store connection
        self.active_connections[user_id][connection_id] = websocket
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "agent_type": agent_type,
            "connected_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Subscribe to agent if specified
        if agent_type:
            self.agent_subscriptions[user_id][agent_type].add(connection_id)
    
    def disconnect(self, connection_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            connection_id: Connection identifier to remove
        """
        if connection_id not in self.connection_metadata:
            return
        
        metadata = self.connection_metadata[connection_id]
        user_id = metadata["user_id"]
        agent_type = metadata.get("agent_type")
        
        # Remove from active connections
        if user_id in self.active_connections:
            self.active_connections[user_id].pop(connection_id, None)
            
            # Clean up empty user dict
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from agent subscriptions
        if agent_type and user_id in self.agent_subscriptions:
            if agent_type in self.agent_subscriptions[user_id]:
                self.agent_subscriptions[user_id][agent_type].discard(connection_id)
                
                # Clean up empty sets
                if not self.agent_subscriptions[user_id][agent_type]:
                    del self.agent_subscriptions[user_id][agent_type]
            
            # Clean up empty user dict
            if not self.agent_subscriptions[user_id]:
                del self.agent_subscriptions[user_id]
        
        # Remove metadata
        del self.connection_metadata[connection_id]
    
    async def send_personal_message(
        self,
        message: Dict[str, Any],
        websocket: WebSocket
    ):
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            message: Message data to send
            websocket: WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            # Connection might be closed
            pass
    
    async def broadcast_to_user(
        self,
        user_id: int,
        message: Dict[str, Any]
    ):
        """
        Broadcast a message to all connections for a specific user.
        
        Args:
            user_id: User ID to broadcast to
            message: Message data to send
        """
        if user_id not in self.active_connections:
            return
        
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Send to all user connections
        disconnected = []
        for connection_id, websocket in self.active_connections[user_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                # Mark for disconnection
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def broadcast_to_agent_subscribers(
        self,
        user_id: int,
        agent_type: str,
        message: Dict[str, Any]
    ):
        """
        Broadcast a message to all connections subscribed to a specific agent.
        
        Args:
            user_id: User ID
            agent_type: Agent type
            message: Message data to send
        """
        if user_id not in self.agent_subscriptions:
            return
        
        if agent_type not in self.agent_subscriptions[user_id]:
            return
        
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Send to all subscribed connections
        disconnected = []
        for connection_id in self.agent_subscriptions[user_id][agent_type]:
            if connection_id in self.active_connections[user_id]:
                websocket = self.active_connections[user_id][connection_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    # Mark for disconnection
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def broadcast_agent_status_change(
        self,
        user_id: int,
        agent_type: str,
        status: str,
        current_task_id: Optional[int] = None,
        tasks_in_queue: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast an agent status change to all relevant connections.
        
        Args:
            user_id: User ID
            agent_type: Agent type
            status: New status (available, busy, idle)
            current_task_id: Current task ID if busy
            tasks_in_queue: Number of tasks in queue
            metadata: Optional additional metadata
        """
        message = {
            "type": "agent_status_change",
            "agent_type": agent_type,
            "status": status,
            "current_task_id": current_task_id,
            "tasks_in_queue": tasks_in_queue,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if metadata:
            message["metadata"] = metadata
        
        # Broadcast to all user connections
        await self.broadcast_to_user(user_id, message)
    
    async def broadcast_task_status_change(
        self,
        user_id: int,
        task_id: str,
        agent_type: str,
        status: str,
        message_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast a task status change to all relevant connections.
        
        Args:
            user_id: User ID
            task_id: Task ID
            agent_type: Agent type
            status: New task status
            message_text: Optional message about the status change
            metadata: Optional additional metadata
        """
        message = {
            "type": "task_status_change",
            "task_id": task_id,
            "agent_type": agent_type,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if message_text:
            message["message"] = message_text
        
        if metadata:
            message["metadata"] = metadata
        
        # Broadcast to all user connections
        await self.broadcast_to_user(user_id, message)
    
    async def broadcast_task_completion(
        self,
        user_id: int,
        task_id: str,
        agent_type: str,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Broadcast a task completion notification.
        
        Args:
            user_id: User ID
            task_id: Task ID
            agent_type: Agent type
            success: Whether task completed successfully
            result: Task result data if successful
            error: Error message if failed
        """
        message = {
            "type": "task_completion",
            "task_id": task_id,
            "agent_type": agent_type,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if result:
            message["result"] = result
        
        if error:
            message["error"] = error
        
        # Broadcast to all user connections
        await self.broadcast_to_user(user_id, message)
    
    async def broadcast_queue_update(
        self,
        user_id: int,
        agent_type: str,
        tasks_in_queue: int,
        queue_position: Optional[int] = None
    ):
        """
        Broadcast a queue length update.
        
        Args:
            user_id: User ID
            agent_type: Agent type
            tasks_in_queue: Number of tasks in queue
            queue_position: Optional position in queue for a specific task
        """
        message = {
            "type": "queue_update",
            "agent_type": agent_type,
            "tasks_in_queue": tasks_in_queue,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if queue_position is not None:
            message["queue_position"] = queue_position
        
        # Broadcast to all user connections
        await self.broadcast_to_user(user_id, message)
    
    def get_connection_count(self, user_id: Optional[int] = None) -> int:
        """
        Get the number of active connections.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Number of active connections
        """
        if user_id is not None:
            return len(self.active_connections.get(user_id, {}))
        
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_user_connections(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all connections for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of connection metadata
        """
        if user_id not in self.active_connections:
            return []
        
        connections = []
        for connection_id in self.active_connections[user_id].keys():
            if connection_id in self.connection_metadata:
                connections.append({
                    "connection_id": connection_id,
                    **self.connection_metadata[connection_id]
                })
        
        return connections


# Global connection manager instance
connection_manager = ConnectionManager()

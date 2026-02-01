from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session as DBSession
from typing import Optional
import json
from datetime import datetime, timezone

from app.api.dependencies import get_db
from app.orchestrator import orchestrator_manager
from app.agents import AgentRegistry


router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/agent")
async def agent_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token"),
    session_id: Optional[str] = Query(None, description="Optional session ID to resume")
):
    """
    WebSocket endpoint for real-time agent interaction.
    
    Protocol:
    1. Client connects with authentication token
    2. Client sends messages in JSON format:
       {
           "type": "message",
           "content": "user message",
           "agent_type": "orchestrator"  // optional
       }
    3. Server streams responses in JSON format:
       {
           "type": "text|tool_call|transfer|error|complete",
           "content": "response content",
           "agent_name": "agent_name",
           "metadata": {}
       }
    4. Connection closes when client disconnects or on error
    
    This enables:
    - Real-time streaming of agent responses
    - Token-by-token text generation
    - Tool call notifications
    - Agent transfer notifications
    - Error handling
    """
    await websocket.accept()
    
    try:
        # TODO: Implement proper authentication
        # For now, we'll skip auth validation
        # In production, validate token and get user_id
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "content": "Invalid JSON format",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                continue
            
            # Validate message format
            if not isinstance(message, dict) or "type" not in message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Invalid message format. Expected {type, content}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                continue
            
            # Handle different message types
            if message["type"] == "message":
                await handle_agent_message(websocket, message, session_id)
            elif message["type"] == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Unknown message type: {message['type']}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    except WebSocketDisconnect:
        # Client disconnected normally
        pass
    except Exception as e:
        # Unexpected error
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Server error: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except:
            pass  # Connection might be closed
    finally:
        # Cleanup
        try:
            await websocket.close()
        except:
            pass


async def handle_agent_message(
    websocket: WebSocket,
    message: dict,
    session_id: Optional[str]
):
    """
    Handle an agent message from the client.
    
    Args:
        websocket: WebSocket connection
        message: Message data from client
        session_id: Optional session ID
    """
    content = message.get("content", "")
    agent_type = message.get("agent_type", "orchestrator")
    
    # Validate content
    if not content:
        await websocket.send_json({
            "type": "error",
            "content": "Message content cannot be empty",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        await websocket.send_json({
            "type": "error",
            "content": f"Invalid agent type: {agent_type}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return
    
    # TODO: Implement actual agent execution with streaming
    # For now, send a placeholder response
    
    # Send processing notification
    await websocket.send_json({
        "type": "processing",
        "agent_name": agent_type,
        "content": f"Processing your message with {agent_type}...",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Simulate streaming response
    response_text = f"Agent '{agent_type}' received: {content}"
    
    # Stream response word by word (simulated)
    words = response_text.split()
    for word in words:
        await websocket.send_json({
            "type": "text",
            "content": word + " ",
            "agent_name": agent_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    # Send completion
    await websocket.send_json({
        "type": "complete",
        "agent_name": agent_type,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

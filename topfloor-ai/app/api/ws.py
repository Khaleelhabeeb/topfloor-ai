from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session as DBSession
from typing import Optional, AsyncGenerator
import json
import uuid
from datetime import datetime, timezone
import asyncio

from app.api.dependencies import get_db
from app.core.security import decode_access_token
from app.orchestrator import orchestrator_manager
from app.agents import AgentRegistry, AgentFactory
from app.services.websocket_service import connection_manager
from app.services.agent_status_service import AgentStatusService
from app.services.chat_service import ChatService
from app.services.session_service import SessionService
from app.adk.runner import AgentRunner
from google import genai


router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/status")
async def status_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token"),
    agent_type: Optional[str] = Query(None, description="Optional agent type to subscribe to"),
    db: DBSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time agent status updates.
    
    This endpoint provides:
    - Real-time agent status changes (available/busy/idle)
    - Queue length updates
    - Current task tracking
    - Task status changes
    - Task completion notifications
    
    Protocol:
    1. Client connects with authentication token
    2. Optionally specify agent_type to subscribe to specific agent
    3. Server sends status updates in JSON format:
       {
           "type": "agent_status_change|task_status_change|task_completion|queue_update",
           "agent_type": "finance",
           "status": "busy",
           "current_task_id": 123,
           "tasks_in_queue": 2,
           "timestamp": "2026-02-03T10:00:00Z"
       }
    4. Client can send ping messages to keep connection alive
    5. Connection closes when client disconnects or on error
    """
    # Generate unique connection ID
    connection_id = f"conn_{uuid.uuid4().hex[:16]}"
    
    # Authenticate user
    try:
        payload = decode_access_token(token)
        if payload is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        # Convert user_id to integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return
    
    try:
        # Register connection
        await connection_manager.connect(
            websocket=websocket,
            user_id=user_id,
            connection_id=connection_id,
            agent_type=agent_type
        )
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established for status updates",
            "connection_id": connection_id,
            "subscribed_agent": agent_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Send initial status for all agents or specific agent
        agent_status_service = AgentStatusService(db)
        
        if agent_type:
            # Validate agent type
            if not AgentRegistry.validate_agent_type(agent_type):
                await websocket.send_json({
                    "type": "error",
                    "content": f"Invalid agent type: {agent_type}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                # Send status for specific agent
                status_obj = agent_status_service.get_or_create_status(user_id, agent_type)
                await websocket.send_json({
                    "type": "initial_status",
                    "agent_type": agent_type,
                    "status": status_obj.status.value,
                    "current_task_id": status_obj.current_task_id,
                    "tasks_in_queue": status_obj.tasks_in_queue,
                    "last_active_at": status_obj.last_active_at.isoformat() if status_obj.last_active_at else None,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        else:
            # Send status for all agents
            summary = agent_status_service.get_status_summary(user_id)
            await websocket.send_json({
                "type": "initial_status",
                "summary": summary,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Message loop (for ping/pong and other client messages)
        while True:
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
            
            # Handle ping messages
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif message.get("type") == "get_status":
                # Client requesting current status
                requested_agent = message.get("agent_type", agent_type)
                if requested_agent:
                    if not AgentRegistry.validate_agent_type(requested_agent):
                        await websocket.send_json({
                            "type": "error",
                            "content": f"Invalid agent type: {requested_agent}",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                    else:
                        status_obj = agent_status_service.get_or_create_status(user_id, requested_agent)
                        await websocket.send_json({
                            "type": "status_response",
                            "agent_type": requested_agent,
                            "status": status_obj.status.value,
                            "current_task_id": status_obj.current_task_id,
                            "tasks_in_queue": status_obj.tasks_in_queue,
                            "last_active_at": status_obj.last_active_at.isoformat() if status_obj.last_active_at else None,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                else:
                    summary = agent_status_service.get_status_summary(user_id)
                    await websocket.send_json({
                        "type": "status_response",
                        "summary": summary,
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
        # Cleanup - unregister connection
        connection_manager.disconnect(connection_id)
        try:
            await websocket.close()
        except:
            pass


@router.websocket("/chat")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token"),
    agent_type: str = Query("orchestrator", description="Agent type to chat with"),
    session_id: Optional[str] = Query(None, description="Optional session ID to resume"),
    db: DBSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time agent chat with message streaming.
    
    This endpoint provides:
    - Real-time streaming of agent responses (token-by-token)
    - Typing indicators
    - Tool call notifications
    - Agent transfer notifications
    - Error handling
    - Conversation history persistence
    
    Protocol:
    1. Client connects with authentication token
    2. Client sends messages in JSON format:
       {
           "type": "message",
           "content": "user message"
       }
    3. Server streams responses in JSON format:
       {
           "type": "typing|text|tool_call|transfer|error|complete",
           "content": "response content",
           "agent_name": "agent_name",
           "metadata": {}
       }
    4. Connection closes when client disconnects or on error
    """
    # Generate unique connection ID
    connection_id = f"conn_{uuid.uuid4().hex[:16]}"
    
    # Authenticate user
    try:
        payload = decode_access_token(token)
        if payload is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        # Convert user_id to integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return
    
    # Validate agent type
    if not AgentRegistry.validate_agent_type(agent_type):
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason=f"Invalid agent type: {agent_type}")
        return
    
    try:
        # Register connection
        await connection_manager.connect(
            websocket=websocket,
            user_id=user_id,
            connection_id=connection_id,
            agent_type=agent_type
        )
        
        # Initialize services
        chat_service = ChatService(db)
        
        # Get or create session
        if session_id:
            # Try to resume existing session
            db_session = SessionService.get_session_by_id(db, session_id, user_id)
            if not db_session or db_session.user_id != user_id or db_session.agent_type != agent_type:
                # Invalid session, create new one
                from app.schemas.session import SessionCreate
                session_create = SessionCreate(
                    agent_type=agent_type,
                    agent_name=AgentRegistry.get_agent_name(agent_type)
                )
                db_session = SessionService.create_session(db, user_id, session_create)
                session_id = db_session.session_id
        else:
            # Create new session
            from app.schemas.session import SessionCreate
            session_create = SessionCreate(
                agent_type=agent_type,
                agent_name=AgentRegistry.get_agent_name(agent_type)
            )
            db_session = SessionService.create_session(db, user_id, session_create)
            session_id = db_session.session_id
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to {AgentRegistry.get_agent_name(agent_type)}",
            "connection_id": connection_id,
            "session_id": session_id,
            "agent_type": agent_type,
            "agent_name": AgentRegistry.get_agent_name(agent_type),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Send conversation history if resuming session
        if session_id and db_session:
            messages, _ = chat_service.get_messages_by_session(
                session_id=db_session.id,  # Use database ID
                user_id=user_id,
                limit=50
            )
            if messages:
                await websocket.send_json({
                    "type": "history",
                    "messages": [
                        {
                            "role": msg.role.value,
                            "content": msg.content,
                            "timestamp": msg.created_at.isoformat()
                        }
                        for msg in reversed(messages)  # Oldest first
                    ],
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
                await handle_chat_message(
                    websocket=websocket,
                    message=message,
                    user_id=user_id,
                    agent_type=agent_type,
                    session_id=session_id,
                    session_db_id=db_session.id,
                    db=db
                )
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
        # Cleanup - unregister connection
        connection_manager.disconnect(connection_id)
        try:
            await websocket.close()
        except:
            pass


async def handle_chat_message(
    websocket: WebSocket,
    message: dict,
    user_id: int,
    agent_type: str,
    session_id: str,
    session_db_id: int,
    db: DBSession
):
    """
    Handle a chat message from the client with streaming response.
    
    Args:
        websocket: WebSocket connection
        message: Message data from client
        user_id: User ID
        agent_type: Agent type
        session_id: Session ID (string)
        session_db_id: Session database ID (integer)
        db: Database session
    """
    content = message.get("content", "")
    
    # Validate content
    if not content:
        await websocket.send_json({
            "type": "error",
            "content": "Message content cannot be empty",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return
    
    # Initialize services
    chat_service = ChatService(db)
    agent_status_service = AgentStatusService(db)
    
    # Store user message
    user_msg = chat_service.create_message(
        session_id=session_db_id,  # Use database ID
        user_id=user_id,
        agent_type=agent_type,
        role="user",
        content=content
    )
    
    try:
        # Send typing indicator
        await websocket.send_json({
            "type": "typing",
            "agent_name": AgentRegistry.get_agent_name(agent_type),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Update agent status to busy
        agent_status_service.set_busy(user_id, agent_type, None)
        
        # Broadcast status change
        await connection_manager.broadcast_agent_status_change(
            user_id=user_id,
            agent_type=agent_type,
            status="busy",
            tasks_in_queue=0
        )
        
        # Create agent
        agent = AgentFactory.create_agent(agent_type)
        
        # Create agent runner
        runner = AgentRunner(
            agent=agent,
            session_id=session_id,
            user_id=user_id,
            agent_type=agent_type,
            enable_memory=True
        )
        
        # Stream agent response
        response_text = ""
        async for chunk in stream_agent_response(runner, content):
            if chunk["type"] == "text":
                response_text += chunk["content"]
                await websocket.send_json({
                    "type": "text",
                    "content": chunk["content"],
                    "agent_name": AgentRegistry.get_agent_name(agent_type),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif chunk["type"] == "tool_call":
                await websocket.send_json({
                    "type": "tool_call",
                    "tool_name": chunk.get("tool_name", "unknown"),
                    "agent_name": AgentRegistry.get_agent_name(agent_type),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif chunk["type"] == "error":
                await websocket.send_json({
                    "type": "error",
                    "content": chunk["content"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                return
        
        # Store agent response
        agent_msg = chat_service.create_message(
            session_id=session_db_id,  # Use database ID
            user_id=user_id,
            agent_type=agent_type,
            role="agent",
            content=response_text
        )
        
        # Send completion
        await websocket.send_json({
            "type": "complete",
            "agent_name": AgentRegistry.get_agent_name(agent_type),
            "session_id": session_id,
            "message_id": agent_msg.message_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Update agent status to available
        agent_status_service.set_available(user_id, agent_type)
        
        # Broadcast status change
        await connection_manager.broadcast_agent_status_change(
            user_id=user_id,
            agent_type=agent_type,
            status="available",
            tasks_in_queue=0
        )
        
    except Exception as e:
        # Handle error
        await websocket.send_json({
            "type": "error",
            "content": f"Failed to process message: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Update agent status to available
        try:
            agent_status_service.set_available(user_id, agent_type)
            await connection_manager.broadcast_agent_status_change(
                user_id=user_id,
                agent_type=agent_type,
                status="available",
                tasks_in_queue=0
            )
        except:
            pass


async def stream_agent_response(runner: AgentRunner, message: str) -> AsyncGenerator[dict, None]:
    """
    Stream agent response token by token.
    
    Args:
        runner: Agent runner instance
        message: User message
        
    Yields:
        Dictionary with chunk type and content
    """
    try:
        # Get ADK session ID
        adk_session_id = await runner._ensure_adk_session_async()
        
        # Retrieve relevant memories if enabled
        relevant_memories = []
        if runner.enable_memory and runner.agent_type:
            relevant_memories = runner.memory_service.search(
                query=message,
                user_id=runner.user_id_int,
                agent_type=runner.agent_type,
                limit=3
            )
        
        # Augment message with memories
        augmented_message = runner._augment_message_with_memories(message, relevant_memories)
        
        # Create content from message
        content = genai.types.Content(
            parts=[genai.types.Part(text=augmented_message)]
        )
        
        # Stream response from agent
        full_response = ""
        async for event in runner.runner.run_async(
            user_id=runner.user_id,
            session_id=adk_session_id,
            new_message=content
        ):
            # Extract text from event
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            # Stream text chunk
                            full_response += part.text
                            yield {
                                "type": "text",
                                "content": part.text
                            }
                        elif hasattr(part, 'function_call'):
                            # Tool call notification
                            yield {
                                "type": "tool_call",
                                "tool_name": part.function_call.name if hasattr(part.function_call, 'name') else "unknown"
                            }
        
        # Store interaction in memory if enabled
        if runner.enable_memory and runner.agent_type:
            runner._store_interaction_memory(message, full_response)
        
    except Exception as e:
        yield {
            "type": "error",
            "content": str(e)
        }


@router.websocket("/agent")
async def agent_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token"),
    session_id: Optional[str] = Query(None, description="Optional session ID to resume")
):
    """
    Legacy WebSocket endpoint for agent interaction (deprecated).
    Use /ws/chat instead for better functionality.
    
    This endpoint is maintained for backward compatibility.
    """
    await websocket.accept()
    
    try:
        # Authenticate user
        payload = decode_access_token(token)
        if payload is None:
            await websocket.send_json({
                "type": "error",
                "content": "Invalid authentication token",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            await websocket.close()
            return
        
        # Send deprecation notice
        await websocket.send_json({
            "type": "warning",
            "message": "This endpoint is deprecated. Please use /ws/chat instead.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
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
            
            # Handle ping messages
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "content": "Please use /ws/chat endpoint for agent interaction",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Server error: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass

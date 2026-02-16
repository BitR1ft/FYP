"""
AI Agent API Endpoints

Provides REST and WebSocket endpoints for agent interactions.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import uuid
import json

from ..agent import Agent, Phase
from ..websocket.manager import get_connection_manager, ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message to send to the agent")
    thread_id: Optional[str] = Field(None, description="Thread ID for conversation continuity")
    project_id: Optional[str] = Field(None, description="Project ID for context")
    model_provider: str = Field("openai", description="LLM provider (openai or anthropic)")
    model_name: str = Field("gpt-4", description="Model name")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Agent's response")
    thread_id: str = Field(..., description="Thread ID for this conversation")
    phase: str = Field(..., description="Current operational phase")


class AgentStatus(BaseModel):
    """Agent status model"""
    available: bool = Field(..., description="Whether agent is available")
    model_providers: list = Field(..., description="Available LLM providers")
    default_model: str = Field(..., description="Default model name")


# Global agent instances (keyed by thread_id)
active_agents: Dict[str, Agent] = {}


@router.get("/status", response_model=AgentStatus)
async def get_agent_status():
    """
    Get agent availability status.
    
    Returns information about available LLM providers and models.
    """
    return AgentStatus(
        available=True,
        model_providers=["openai", "anthropic"],
        default_model="gpt-4"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a message to the agent and get a response (non-streaming).
    
    This endpoint is useful for simple request/response interactions.
    For streaming responses, use the WebSocket endpoint.
    """
    try:
        # Get or create agent for this thread
        thread_id = request.thread_id or str(uuid.uuid4())
        
        if thread_id not in active_agents:
            active_agents[thread_id] = Agent(
                model_provider=request.model_provider,
                model_name=request.model_name,
                enable_memory=True
            )
        
        agent = active_agents[thread_id]
        
        # Chat with agent
        result = await agent.chat(
            message=request.message,
            thread_id=thread_id
        )
        
        # Extract agent's response from messages
        agent_messages = [
            msg.content for msg in result["messages"]
            if msg.type == "ai" and not msg.content.startswith("THOUGHT:")
        ]
        
        response_text = agent_messages[-1] if agent_messages else "No response generated."
        
        return ChatResponse(
            response=response_text,
            thread_id=thread_id,
            phase=result["current_phase"]
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{client_id}")
async def agent_websocket(
    websocket: WebSocket,
    client_id: str,
    connection_manager: ConnectionManager = Depends(get_connection_manager)
):
    """
    WebSocket endpoint for streaming agent interactions.
    
    Provides real-time streaming of:
    - Agent thoughts (reasoning)
    - Tool executions
    - Final responses
    
    Expected message format from client:
    {
        "type": "chat",
        "message": "Your message here",
        "thread_id": "optional-thread-id",
        "project_id": "optional-project-id",
        "model_provider": "openai",
        "model_name": "gpt-4"
    }
    """
    await websocket.accept()
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "Agent WebSocket connected"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "chat":
                # Extract parameters
                user_message = data.get("message")
                thread_id = data.get("thread_id") or str(uuid.uuid4())
                project_id = data.get("project_id")
                model_provider = data.get("model_provider", "openai")
                model_name = data.get("model_name", "gpt-4")
                
                # Get or create agent
                if thread_id not in active_agents:
                    active_agents[thread_id] = Agent(
                        model_provider=model_provider,
                        model_name=model_name,
                        enable_memory=True
                    )
                
                agent = active_agents[thread_id]
                
                # Stream agent's response
                try:
                    async for chunk in agent.stream_chat(
                        message=user_message,
                        thread_id=thread_id
                    ):
                        # Send each state update to client
                        await websocket.send_json({
                            "type": "agent_update",
                            "thread_id": thread_id,
                            "data": {
                                "node": list(chunk.keys())[0] if chunk else "unknown",
                                "state_update": {
                                    k: str(v) if not isinstance(v, (dict, list, str, int, float, bool, type(None))) else v
                                    for k, v in (list(chunk.values())[0] if chunk else {}).items()
                                }
                            }
                        })
                    
                    # Send completion message
                    await websocket.send_json({
                        "type": "agent_complete",
                        "thread_id": thread_id,
                        "message": "Agent processing complete"
                    })
                    
                except Exception as e:
                    logger.error(f"Error in agent streaming: {e}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif message_type == "ping":
                # Respond to ping
                await websocket.send_json({"type": "pong"})
            
            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"Agent WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in agent WebSocket: {e}", exc_info=True)
    finally:
        # Cleanup if needed
        pass

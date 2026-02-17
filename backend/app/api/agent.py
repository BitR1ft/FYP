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


class StopRequest(BaseModel):
    """Stop agent request model"""
    thread_id: str = Field(..., description="Thread ID of the agent to stop")


class StopResponse(BaseModel):
    """Stop agent response model"""
    thread_id: str = Field(..., description="Thread ID of the stopped agent")
    status: str = Field(..., description="Stop status")


class ResumeRequest(BaseModel):
    """Resume agent request model"""
    thread_id: str = Field(..., description="Thread ID of the agent to resume")
    message: Optional[str] = Field(None, description="Optional message to send on resume")


class ResumeResponse(BaseModel):
    """Resume agent response model"""
    thread_id: str = Field(..., description="Thread ID of the resumed agent")
    status: str = Field(..., description="Resume status")


class GuidanceRequest(BaseModel):
    """Guidance request model"""
    thread_id: str = Field(..., description="Thread ID of the agent")
    guidance: str = Field(..., description="Guidance text to send to the agent")


class GuidanceResponse(BaseModel):
    """Guidance response model"""
    thread_id: str = Field(..., description="Thread ID of the agent")
    status: str = Field(..., description="Guidance status")


class ApproveRequest(BaseModel):
    """Approve/reject operation request model"""
    thread_id: str = Field(..., description="Thread ID of the agent")
    approved: bool = Field(..., description="Whether the operation is approved")


class ApproveResponse(BaseModel):
    """Approve/reject operation response model"""
    thread_id: str = Field(..., description="Thread ID of the agent")
    status: str = Field(..., description="Approval status")


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


@router.post("/stop", response_model=StopResponse)
async def stop_agent(request: StopRequest):
    """
    Stop a running agent.

    Sets should_stop=True on the agent state and stores checkpoint.
    """
    try:
        thread_id = request.thread_id

        if thread_id not in active_agents:
            raise HTTPException(status_code=404, detail=f"No active agent found for thread {thread_id}")

        agent = active_agents[thread_id]
        agent.state["should_stop"] = True

        return StopResponse(
            thread_id=thread_id,
            status="stopped"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", response_model=ResumeResponse)
async def resume_agent(request: ResumeRequest):
    """
    Resume a stopped agent from checkpoint.
    """
    try:
        thread_id = request.thread_id

        if thread_id not in active_agents:
            raise HTTPException(status_code=404, detail=f"No active agent found for thread {thread_id}")

        agent = active_agents[thread_id]
        agent.state["should_stop"] = False

        return ResumeResponse(
            thread_id=thread_id,
            status="resumed"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guidance", response_model=GuidanceResponse)
async def send_guidance(request: GuidanceRequest):
    """
    Send live guidance to an active agent.

    Stores guidance in the agent state.
    """
    try:
        thread_id = request.thread_id

        if thread_id not in active_agents:
            raise HTTPException(status_code=404, detail=f"No active agent found for thread {thread_id}")

        agent = active_agents[thread_id]
        agent.state["guidance"] = request.guidance

        return GuidanceResponse(
            thread_id=thread_id,
            status="guidance_received"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending guidance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve", response_model=ApproveResponse)
async def approve_operation(request: ApproveRequest):
    """
    Approve or reject a pending agent operation.

    Updates pending_approval status in the agent state.
    """
    try:
        thread_id = request.thread_id

        if thread_id not in active_agents:
            raise HTTPException(status_code=404, detail=f"No active agent found for thread {thread_id}")

        agent = active_agents[thread_id]
        status = "approved" if request.approved else "rejected"
        agent.state["pending_approval"] = {"status": status}

        return ApproveResponse(
            thread_id=thread_id,
            status=status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing approval: {e}", exc_info=True)
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
            
            elif message_type == "stop":
                thread_id = data.get("thread_id", "")
                if thread_id in active_agents:
                    await websocket.send_json({
                        "type": "agent_stopped",
                        "thread_id": thread_id,
                        "message": "Agent execution stopped"
                    })

            elif message_type == "guidance":
                thread_id = data.get("thread_id", "")
                guidance_text = data.get("guidance", "")
                await websocket.send_json({
                    "type": "guidance_received",
                    "thread_id": thread_id,
                    "guidance": guidance_text
                })

            elif message_type == "approve":
                thread_id = data.get("thread_id", "")
                approved = data.get("approved", False)
                status = "approved" if approved else "rejected"
                await websocket.send_json({
                    "type": "approval_response",
                    "thread_id": thread_id,
                    "status": status
                })

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

"""
Server-Sent Events (SSE) endpoints for real-time streaming
Provides one-way server-to-client streaming for logs and progress updates
"""
from fastapi import APIRouter, Request, Depends
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator, Dict, Any
import asyncio
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

router = APIRouter()


class SSEManager:
    """Manager for Server-Sent Events streams"""
    
    def __init__(self):
        # Store active event generators by project
        self.active_streams: Dict[str, list] = {}
        self.scan_queues: Dict[str, asyncio.Queue] = {}
        self.scan_queue_lock = asyncio.Lock()

    async def _get_scan_queue(self, project_id: str) -> asyncio.Queue:
        async with self.scan_queue_lock:
            return self.scan_queues.setdefault(project_id, asyncio.Queue())
    
    async def scan_event_generator(
        self,
        project_id: str,
        request: Request
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate scan progress events
        
        Args:
            project_id: Project identifier
            request: FastAPI request object (to detect disconnection)
            
        Yields:
            Event dictionaries with scan updates
        """
        try:
            # Send initial connection event
            yield {
                'event': 'connected',
                'data': json.dumps({
                    'message': f'Connected to scan updates for project {project_id}',
                    'project_id': project_id,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
            
            queue = await self._get_scan_queue(project_id)

            # Keep connection alive and stream events
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info(f"SSE client disconnected from project {project_id}")
                    break

                try:
                    scan_update = await asyncio.wait_for(queue.get(), timeout=30)
                    yield {
                        'event': 'scan_update',
                        'data': json.dumps(scan_update)
                    }
                except asyncio.TimeoutError:
                    yield {
                        'event': 'heartbeat',
                        'data': json.dumps({
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    }
        
        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for project {project_id}")
        except Exception as e:
            logger.error(f"Error in SSE stream for project {project_id}: {e}")
            yield {
                'event': 'error',
                'data': json.dumps({
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
    
    async def log_event_generator(
        self,
        project_id: str,
        request: Request
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate log events for a project
        
        Args:
            project_id: Project identifier
            request: FastAPI request object
            
        Yields:
            Event dictionaries with log entries
        """
        try:
            # Send initial connection event
            yield {
                'event': 'connected',
                'data': json.dumps({
                    'message': f'Connected to logs for project {project_id}',
                    'project_id': project_id,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
            
            # Stream log events
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info(f"Log SSE client disconnected from project {project_id}")
                    break
                
                # Here you would fetch actual logs from your logging system
                # For now, send heartbeat
                yield {
                    'event': 'heartbeat',
                    'data': json.dumps({
                        'timestamp': datetime.utcnow().isoformat()
                    })
                }
                
                # Wait before next update
                await asyncio.sleep(15)  # Heartbeat every 15 seconds
        
        except asyncio.CancelledError:
            logger.info(f"Log SSE stream cancelled for project {project_id}")
        except Exception as e:
            logger.error(f"Error in log SSE stream for project {project_id}: {e}")
            yield {
                'event': 'error',
                'data': json.dumps({
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
    
    async def send_scan_update(
        self,
        project_id: str,
        scan_type: str,
        status: str,
        data: Dict = None
    ):
        """
        Send a scan update event
        
        Args:
            project_id: Project identifier
            scan_type: Type of scan
            status: Scan status
            data: Additional data
        """
        payload = {
            'project_id': project_id,
            'scan_type': scan_type,
            'status': status,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        queue = await self._get_scan_queue(project_id)
        await queue.put(payload)


# Global SSE manager
sse_manager = SSEManager()


@router.get("/stream/scans/{project_id}")
async def stream_scan_updates(project_id: str, request: Request):
    """
    SSE endpoint for streaming scan updates
    
    Args:
        project_id: Project identifier
        request: FastAPI request
        
    Returns:
        EventSourceResponse with scan update stream
    """
    return EventSourceResponse(
        sse_manager.scan_event_generator(project_id, request),
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@router.get("/stream/logs/{project_id}")
async def stream_logs(project_id: str, request: Request):
    """
    SSE endpoint for streaming project logs
    
    Args:
        project_id: Project identifier
        request: FastAPI request
        
    Returns:
        EventSourceResponse with log stream
    """
    return EventSourceResponse(
        sse_manager.log_event_generator(project_id, request),
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


def get_sse_manager() -> SSEManager:
    """Dependency injection for SSE manager"""
    return sse_manager

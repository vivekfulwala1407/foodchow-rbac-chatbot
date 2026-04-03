from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import process_chat_query
from app.chat.streaming import stream_rag_response

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Standard (non-streaming) chat endpoint. Kept for compatibility."""
    history = None
    if request.chat_history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history
        ]

    result = process_chat_query(
        query=request.query,
        current_user=current_user,
        chat_history=history,
    )
    return ChatResponse(**result)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Streaming chat endpoint using Server-Sent Events.

    Why SSE over WebSockets?
    - SSE is simpler — one direction only (server → client)
    - No handshake overhead
    - Native browser support
    - Perfect for LLM text streaming
    """
    history = None
    if request.chat_history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history
        ]

    return StreamingResponse(
        stream_rag_response(
            query=request.query,
            current_user=current_user,
            chat_history=history,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disables nginx buffering
        },
    )
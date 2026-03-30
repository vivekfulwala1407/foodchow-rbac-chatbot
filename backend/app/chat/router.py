from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import process_chat_query

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Memory-aware chat endpoint.
    Frontend sends full chat history with every request.
    """
    # Convert Pydantic models to plain dicts for pipeline
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
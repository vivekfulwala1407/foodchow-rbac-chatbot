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
    Main chat endpoint — the frontend calls this for every message.

    Protected by JWT — user must be logged in.
    Role is extracted from JWT — no way for user to fake their role.
    RBAC filtering happens inside process_chat_query automatically.
    """
    result = process_chat_query(
        query=request.query,
        current_user=current_user,
    )
    return ChatResponse(**result)
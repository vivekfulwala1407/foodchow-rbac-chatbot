from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[list[ChatMessage]] = []


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    role: str
    departments_searched: list[str]
    chunks_found: int
    query: str
    follow_up_questions: list[str] = []
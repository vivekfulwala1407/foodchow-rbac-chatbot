from pydantic import BaseModel
from typing import Optional


# What frontend sends to /chat/query
class ChatRequest(BaseModel):
    query: str


# What we send back to frontend
class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    role: str
    departments_searched: list[str]
    chunks_found: int
    query: str
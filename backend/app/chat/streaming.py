import json
from typing import AsyncGenerator
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from pydantic import SecretStr

from app.config import get_settings
from app.rag.vector_store import search_documents
from app.rag.prompts import build_rag_prompt, build_no_results_prompt
from app.rbac.permissions import verify_access
from app.auth.schemas import CurrentUser
from app.utils.logger import log_query

settings = get_settings()


def format_sse(data: dict) -> str:
    """
    Formats data as Server-Sent Event string.

    SSE format:
    data: {"type": "token", "content": "Hello"}\\n\\n

    The double newline is required by the SSE spec.
    """
    return f"data: {json.dumps(data)}\n\n"


async def stream_rag_response(
    query: str,
    current_user: CurrentUser,
    chat_history: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    """
    Async generator that streams LLM response token by token.

    Yields SSE-formatted strings:
    - type: "metadata" → sources, departments (sent first)
    - type: "token"    → each word/chunk of the answer
    - type: "done"     → signals stream is complete
    - type: "error"    → if something goes wrong
    """
    try:
        # ── Step 1: RBAC ──────────────────────────────────────────
        allowed_departments = verify_access(current_user)

        # ── Step 2: Enhanced search query with memory ─────────────
        search_query = query
        if chat_history and len(chat_history) >= 2:
            last_user_msg = next(
                (m["content"] for m in reversed(chat_history)
                 if m["role"] == "user"), ""
            )
            if last_user_msg and last_user_msg != query:
                search_query = f"{last_user_msg} {query}"

        # ── Step 3: Vector search ──────────────────────────────────
        retrieved_chunks = search_documents(
            query=search_query,
            allowed_departments=allowed_departments,
            top_k=settings.top_k_results,
        )

        sources = list({chunk["source"] for chunk in retrieved_chunks})

        # ── Step 4: Send metadata first (before streaming starts) ──
        yield format_sse({
            "type": "metadata",
            "sources": sources,
            "departments_searched": allowed_departments,
            "chunks_found": len(retrieved_chunks),
        })

        # ── Step 5: Build prompt ───────────────────────────────────
        if not retrieved_chunks:
            prompt = build_no_results_prompt(
                query=query,
                role=current_user.role,
                chat_history=chat_history,
            )
        else:
            prompt = build_rag_prompt(
                query=query,
                context_chunks=retrieved_chunks,
                role=current_user.role,
                chat_history=chat_history,
            )

        # ── Step 6: Stream from Groq ───────────────────────────────
        llm = ChatGroq(
                    api_key=SecretStr(settings.groq_api_key),
                    model=settings.llm_model,
                    temperature=0.1,
                    max_tokens=1024,
                )

        full_answer = ""

        async for chunk in llm.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                full_answer += str(chunk.content)
                yield format_sse({
                    "type": "token",
                    "content": chunk.content,
                })

        # ── Step 7: Signal completion ──────────────────────────────
        yield format_sse({"type": "done"})

        # ── Step 8: Audit log ──────────────────────────────────────
        log_query(
            username=current_user.username,
            role=current_user.role,
            query=query,
            sources=sources,
            chunks_found=len(retrieved_chunks),
            status="success",
        )

    except Exception as e:
        yield format_sse({
            "type": "error",
            "content": f"Something went wrong: {str(e)}",
        })
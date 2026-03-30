from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from pydantic import SecretStr

from app.config import get_settings
from app.rag.vector_store import search_documents
from app.rag.prompts import build_rag_prompt, build_no_results_prompt
from app.rbac.permissions import verify_access
from app.auth.schemas import CurrentUser

settings = get_settings()


def get_llm() -> ChatGroq:
    return ChatGroq(
        api_key=SecretStr(settings.groq_api_key),
        model=settings.llm_model,
        temperature=0.1,
        max_tokens=1024,
    )


def run_rag_pipeline(
    query: str,
    current_user: CurrentUser,
    chat_history: list[dict] | None = None,
) -> dict:
    """
    Memory-aware RAG pipeline.

    chat_history format:
    [
        {"role": "user", "content": "What was Q3 revenue?"},
        {"role": "assistant", "content": "$4.85M..."},
        ...
    ]
    """

    # ── Step 1: RBAC ────────────────────────────────────────────────
    allowed_departments = verify_access(current_user)

    # ── Step 2: Enhanced query for memory ───────────────────────────
    # If there's history, combine it with current query for better search
    search_query = query
    if chat_history and len(chat_history) >= 2:
        # Take last user message + current query for richer vector search
        last_user_msg = next(
            (m["content"] for m in reversed(chat_history)
             if m["role"] == "user"), ""
        )
        if last_user_msg and last_user_msg != query:
            search_query = f"{last_user_msg} {query}"

    # ── Step 3: Vector search ────────────────────────────────────────
    retrieved_chunks = search_documents(
        query=search_query,
        allowed_departments=allowed_departments,
        top_k=settings.top_k_results,
    )

    # ── Step 4: Handle zero results ──────────────────────────────────
    if not retrieved_chunks:
        no_results_prompt = build_no_results_prompt(
            query=query,
            role=current_user.role,
            chat_history=chat_history,
        )
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=no_results_prompt)])
        return {
            "answer": response.content,
            "sources": [],
            "departments_searched": allowed_departments,
            "chunks_found": 0,
        }

    # ── Step 5: Build memory-aware prompt ────────────────────────────
    prompt = build_rag_prompt(
        query=query,
        context_chunks=retrieved_chunks,
        role=current_user.role,
        chat_history=chat_history,
    )

    # ── Step 6: Call Groq LLM ────────────────────────────────────────
    llm = get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    # ── Step 7: Extract sources ──────────────────────────────────────
    sources = list({chunk["source"] for chunk in retrieved_chunks})

    return {
        "answer": response.content,
        "sources": sources,
        "departments_searched": allowed_departments,
        "chunks_found": len(retrieved_chunks),
    }
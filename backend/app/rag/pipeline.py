from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from pydantic import SecretStr

from app.config import get_settings
from app.rag.vector_store import search_documents
from app.rag.prompts import build_rag_prompt, build_no_results_prompt
from app.rag.followup import generate_follow_up_questions
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
    Full RAG pipeline with follow-up question generation.
    """

    # ── Step 1: RBAC ────────────────────────────────────────────────
    allowed_departments = verify_access(current_user)

    # ── Step 2: Enhanced search query ───────────────────────────────
    search_query = query
    if chat_history and len(chat_history) >= 2:
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
            "follow_up_questions": [],
        }

    # ── Step 5: Build prompt ─────────────────────────────────────────
    prompt = build_rag_prompt(
        query=query,
        context_chunks=retrieved_chunks,
        role=current_user.role,
        chat_history=chat_history,
    )

    # ── Step 6: Call Groq LLM ────────────────────────────────────────
    llm = get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])
    answer: str = str(response.content)

    # ── Step 7: Extract sources ──────────────────────────────────────
    sources = list({chunk["source"] for chunk in retrieved_chunks})

    # ── Step 8: Generate follow-up questions ─────────────────────────
    follow_ups = generate_follow_up_questions(
        query=query,
        answer=answer,
        role=current_user.role,
        sources=sources,
    )

    return {
        "answer": answer,
        "sources": sources,
        "departments_searched": allowed_departments,
        "chunks_found": len(retrieved_chunks),
        "follow_up_questions": follow_ups,
    }
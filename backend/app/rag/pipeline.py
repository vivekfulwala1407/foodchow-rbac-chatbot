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
    """
    Initialize Groq LLM client.

    Why ChatGroq?
    - Uses Groq's inference API — fastest LLM inference available
    - llama-3.3-70b-versatile: best open-source model for Q&A tasks
    - temperature=0.1: near-deterministic responses
      (we want factual answers, not creative ones)
    """
    return ChatGroq(
        api_key=SecretStr(settings.groq_api_key),
        model=settings.llm_model,
        temperature=0.1,
        max_tokens=1024,
    )


def run_rag_pipeline(
    query: str,
    current_user: CurrentUser,
) -> dict:
    """
    Main RAG pipeline — orchestrates the entire query flow.

    Flow:
    1. Get allowed departments for this user's role (RBAC)
    2. Search ChromaDB with role filter
    3. If no results → return polite message
    4. Build prompt with retrieved context
    5. Send to Groq LLM
    6. Return answer + sources

    Returns dict with:
    - answer: the LLM generated response
    - sources: list of source document filenames
    - departments_searched: which departments were searched
    - chunks_found: how many relevant chunks were retrieved
    """

    # ── Step 1: RBAC — get allowed departments ──────────────────────
    allowed_departments = verify_access(current_user)

    # ── Step 2: Vector search with role filter ──────────────────────
    retrieved_chunks = search_documents(
        query=query,
        allowed_departments=allowed_departments,
        top_k=settings.top_k_results,
    )

    # ── Step 3: Handle zero results ─────────────────────────────────
    if not retrieved_chunks:
        no_results_prompt = build_no_results_prompt(
            query=query,
            role=current_user.role,
        )
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=no_results_prompt)])
        return {
            "answer": response.content,
            "sources": [],
            "departments_searched": allowed_departments,
            "chunks_found": 0,
        }

    # ── Step 4: Build prompt with context ───────────────────────────
    prompt = build_rag_prompt(
        query=query,
        context_chunks=retrieved_chunks,
        role=current_user.role,
    )

    # ── Step 5: Call Groq LLM ────────────────────────────────────────
    llm = get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    # ── Step 6: Extract unique source documents ──────────────────────
    sources = list({chunk["source"] for chunk in retrieved_chunks})

    return {
        "answer": response.content,
        "sources": sources,
        "departments_searched": allowed_departments,
        "chunks_found": len(retrieved_chunks),
    }
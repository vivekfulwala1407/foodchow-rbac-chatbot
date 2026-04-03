from app.rag.pipeline import run_rag_pipeline
from app.auth.schemas import CurrentUser
from app.utils.logger import log_query


def process_chat_query(
    query: str,
    current_user: CurrentUser,
    chat_history: list[dict] | None = None,
) -> dict:
    query = query.strip()
    if not query:
        return {
            "answer": "Please enter a valid question.",
            "sources": [],
            "role": current_user.role,
            "departments_searched": [],
            "chunks_found": 0,
            "query": query,
            "follow_up_questions": [],
        }

    result = run_rag_pipeline(
        query=query,
        current_user=current_user,
        chat_history=chat_history,
    )

    log_query(
        username=current_user.username,
        role=current_user.role,
        query=query,
        sources=result["sources"],
        chunks_found=result["chunks_found"],
        status="success",
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "role": current_user.role,
        "departments_searched": result["departments_searched"],
        "chunks_found": result["chunks_found"],
        "query": query,
        "follow_up_questions": result.get("follow_up_questions", []),
    }
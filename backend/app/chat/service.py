from app.rag.pipeline import run_rag_pipeline
from app.auth.schemas import CurrentUser
from app.utils.logger import log_query


def process_chat_query(
    query: str,
    current_user: CurrentUser,
) -> dict:
    """
    Orchestrates a chat query end to end.

    1. Runs the RAG pipeline
    2. Logs the query to audit trail
    3. Returns structured response
    """

    # Validate query is not empty
    query = query.strip()
    if not query:
        return {
            "answer": "Please enter a valid question.",
            "sources": [],
            "role": current_user.role,
            "departments_searched": [],
            "chunks_found": 0,
            "query": query,
        }

    # Run the full RAG pipeline
    result = run_rag_pipeline(
        query=query,
        current_user=current_user,
    )

    # Write to audit log
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
    }
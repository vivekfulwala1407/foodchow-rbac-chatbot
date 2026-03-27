import chromadb
import numpy as np
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.config import get_settings

settings = get_settings()

# Load embedding model once at module level
print("Loading embedding model...")
embedding_model = SentenceTransformer(settings.embedding_model)
print("Embedding model loaded.")


def get_chroma_client():
    """Returns a persistent ChromaDB client (data saved to disk)."""
    return chromadb.PersistentClient(
        path=settings.chroma_db_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection():
    """Gets or creates the main ChromaDB collection."""
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def add_documents(
    chunks: list[str],
    metadatas: list[dict],
    ids: list[str],
) -> None:
    """
    Embeds chunks and stores them in ChromaDB with metadata.

    The metadata (department, source) enables role-based filtering.
    Without metadata we couldn't restrict searches by department.
    """
    collection = get_collection()

    # encode() returns numpy array — convert to plain Python nested list
    embeddings = np.array(embedding_model.encode(chunks)).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,  # type: ignore[arg-type]
        metadatas=metadatas,    # type: ignore[arg-type]
        ids=ids,
    )


def search_documents(
    query: str,
    allowed_departments: list[str],
    top_k: int = 5,
) -> list[dict]:
    """
    Searches ChromaDB for relevant chunks filtered by allowed departments.

    This is where RBAC enforcement happens at the data layer.
    The 'where' filter ensures only permitted department docs are ever fetched.

    Returns list of dicts with 'content', 'source', 'department'.
    """
    collection = get_collection()

    # Embed the query with the same model used during ingestion
    query_embedding: list[float] = np.array(
        embedding_model.encode([query])
    )[0].tolist()

    # Build the department filter
    # Single department → simple equality
    # Multiple departments → $in operator
    if len(allowed_departments) == 1:
        where_filter: dict = {"department": allowed_departments[0]}
    else:
        where_filter = {"department": {"$in": allowed_departments}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    # Format results into clean list of dicts
    formatted: list[dict] = []

    documents = results.get("documents") or []
    metadatas_result = results.get("metadatas") or []
    distances = results.get("distances") or []

    if documents and documents[0]:
        for doc, meta, dist in zip(
            documents[0],
            metadatas_result[0],
            distances[0],
        ):
            formatted.append({
                "content": doc,
                "source": meta.get("source", "Unknown"),
                "department": meta.get("department", "Unknown"),
                "relevance_score": round(1 - dist, 4),
            })

    return formatted


def get_collection_stats() -> dict:
    """Returns stats about the current collection — useful for debugging."""
    collection = get_collection()
    count = collection.count()
    return {
        "collection_name": settings.chroma_collection_name,
        "total_chunks": count,
    }
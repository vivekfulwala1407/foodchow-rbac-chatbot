import os
import sys

# Add backend/ to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.chunker import split_text
from app.rag.vector_store import add_documents, get_collection_stats
from app.config import get_settings

settings = get_settings()

# Maps folder name → department label stored in metadata
DEPARTMENT_MAP = {
    "finance": "finance",
    "marketing": "marketing",
    "hr": "hr",
    "engineering": "engineering",
    "general": "general",
}


def load_text_file(filepath: str) -> str:
    """Read a .txt file and return its content."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def ingest_all_documents(data_dir: str) -> None:
    """
    Walks through all department folders, reads documents,
    splits into chunks, and stores in ChromaDB with metadata.
    
    Each chunk gets:
    - department: which folder it came from
    - source: original filename
    - chunk_id: unique ID for deduplication
    """
    print("\n========================================")
    print("  FoodChow Document Ingestion Pipeline")
    print("========================================\n")

    total_chunks = 0

    for folder_name, department_label in DEPARTMENT_MAP.items():
        folder_path = os.path.join(data_dir, folder_name)

        if not os.path.exists(folder_path):
            print(f"[SKIP] Folder not found: {folder_path}")
            continue

        files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

        if not files:
            print(f"[SKIP] No .txt files in {folder_name}/")
            continue

        print(f"[{department_label.upper()}] Processing {len(files)} file(s)...")

        for filename in files:
            filepath = os.path.join(folder_path, filename)
            text = load_text_file(filepath)

            # Split document into chunks
            chunks = split_text(text)

            # Build metadata and IDs for each chunk
            metadatas = []
            ids = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{department_label}_{filename}_{i}"
                metadatas.append({
                    "department": department_label,
                    "source": filename,
                })
                ids.append(chunk_id)

            # Store in ChromaDB
            add_documents(chunks, metadatas, ids)

            total_chunks += len(chunks)
            print(f"  ✓ {filename} → {len(chunks)} chunks ingested")

    print(f"\n========================================")
    print(f"  Ingestion Complete!")

    # Show final stats
    stats = get_collection_stats()
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Total chunks in DB: {stats['total_chunks']}")
    print(f"========================================\n")


if __name__ == "__main__":
    # data/ folder is at backend/data/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    ingest_all_documents(data_dir)
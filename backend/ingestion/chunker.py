from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import get_settings

settings = get_settings()


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    RecursiveCharacterTextSplitter is the best general-purpose splitter.

    It tries to split on paragraphs first, then sentences, then words —
    so chunks are semantically meaningful, not cut mid-sentence.

    chunk_size: max characters per chunk
    chunk_overlap: characters shared between consecutive chunks
                   (overlap ensures context is not lost at boundaries)
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )


def split_text(text: str) -> list[str]:
    """Split a document string into chunks."""
    splitter = get_text_splitter()
    return splitter.split_text(text)
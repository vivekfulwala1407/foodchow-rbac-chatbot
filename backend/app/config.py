from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "FoodChow RBAC Chatbot"
    app_version: str = "1.0.0"
    debug: bool = True

    # Groq
    groq_api_key: str = ""

    # JWT
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8

    # ChromaDB
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "foodchow_docs"

    # RAG
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.3-70b-versatile"
    top_k_results: int = 5
    chunk_size: int = 800
    chunk_overlap: int = 150

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
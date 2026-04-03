from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,      # checks connection before using it
    pool_size=10,            # max 10 connections in pool
    max_overflow=20,         # allow 20 extra connections under load
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency — provides a DB session per request.
    Always closes the session after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
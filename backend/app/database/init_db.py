import uuid
import bcrypt
from sqlalchemy.orm import Session

from app.database.connection import engine, SessionLocal
from app.database.models import Base, User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def init_database() -> None:
    """
    Creates all tables and seeds super_admin on first run.
    Safe to call on every startup — checks before inserting.

    Why PostgreSQL over SQLite?
    - Handles concurrent connections properly
    - Industry standard for production apps
    - Better data types, constraints, and indexing
    - UUID generation built-in (gen_random_uuid)
    """
    print("Initializing database...")

    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(
            User.username == "super_admin"
        ).first()

        if not existing:
            super_admin = User(
                user_id=str(uuid.uuid4()),
                username="super_admin",
                password_hash=hash_password("admin@123"),
                role="super_admin",
                full_name="Super Administrator",
                email="admin@finsolve.com",
                is_active=True,
                created_by="system",
            )
            db.add(super_admin)
            db.commit()
            print("Super admin created successfully")
            print("Username: super_admin")
            print("Password: admin@123")
        else:
            print("Database ready — super_admin exists")

    except Exception as e:
        print(f"Database init error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
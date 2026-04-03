import uuid
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import User
from app.auth.schemas import CurrentUser

settings = get_settings()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )


def get_user_by_username(
    username: str,
    db: Session
) -> Optional[User]:
    return db.query(User).filter(
        User.username == username,
        User.is_active == True
    ).first()


def authenticate_user(
    username: str,
    password: str,
    db: Session
) -> Optional[User]:
    user = get_user_by_username(username, db)
    if not user:
        return None
    if not verify_password(password, str(user.password_hash)):
        return None
    return user


def create_access_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.jwt_expire_hours
    )
    payload = {
        "sub": username,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
    except Exception:
        return None
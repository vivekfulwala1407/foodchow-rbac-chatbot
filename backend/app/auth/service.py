import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.auth.schemas import CurrentUser

settings = get_settings()

# Password hashing setup
# Why bcrypt? It's slow by design — makes brute force attacks expensive
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def load_users() -> list[dict]:
    """Load users from users.json file."""
    # Walk up from app/ to find users.json at backend/ level
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    users_file = os.path.join(base_dir, "users.json")

    with open(users_file, "r") as f:
        data = json.load(f)
    return data["users"]


def get_user_by_username(username: str) -> Optional[dict]:
    """Find a user dict by username."""
    users = load_users()
    for user in users:
        if user["username"] == username:
            return user
    return None


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify password against stored value.
    
    In production: stored_password would be a bcrypt hash.
    For this project: we compare plain text (users.json stores plain passwords).
    We keep this function so switching to hashed passwords later is a one-line change.
    """
    return plain_password == stored_password


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Verify credentials and return user dict if valid, else None."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def create_access_token(username: str, role: str) -> str:
    """
    Create a signed JWT token.
    
    JWT structure:
    - Header: algorithm used (HS256)
    - Payload: sub (username), role, exp (expiry time)
    - Signature: signed with JWT_SECRET_KEY — tamper-proof
    """
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.jwt_expire_hours
    )

    payload = {
        "sub": username,        # subject — who this token belongs to
        "role": role,           # their department role
        "exp": expire,          # when this token stops working
        "iat": datetime.now(timezone.utc),  # issued at
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return token


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except Exception:
        return None
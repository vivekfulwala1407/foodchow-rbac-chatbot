from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.service import decode_token, get_user_by_username
from app.auth.schemas import CurrentUser

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """
    FastAPI dependency — validates JWT and returns the current user.

    How it works:
    1. FastAPI extracts the Bearer token from the Authorization header
    2. We decode and validate the JWT
    3. We load the full user record from users.json
    4. We return a CurrentUser object that any route can use

    If anything fails → 401 Unauthorized
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    # typed as Optional[str] — Pylance now knows None is handled below
    username: Optional[str] = payload.get("sub")
    role: Optional[str] = payload.get("role")

    # Explicit None check — after this block, Pylance knows they are str
    if username is None or role is None:
        raise credentials_exception

    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception

    return CurrentUser(
        user_id=user["user_id"],
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        email=user["email"],
    )
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth.service import decode_token, get_user_by_username
from app.auth.schemas import CurrentUser
from app.database.connection import get_db

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    username: Optional[str] = payload.get("sub")
    role: Optional[str] = payload.get("role")

    if username is None or role is None:
        raise credentials_exception

    user = get_user_by_username(username, db)
    if user is None:
        raise credentials_exception

    return CurrentUser(
        user_id=str(user.user_id),
        username=str(user.username),
        full_name=str(user.full_name),
        role=str(user.role),
        email=str(user.email),
    )
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, LoginResponse, CurrentUser
from app.auth.service import authenticate_user, create_access_token
from app.auth.dependencies import get_current_user
from app.database.connection import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = authenticate_user(request.username, request.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token(
        username=str(user.username),
        role=str(user.role),
    )

    return LoginResponse(
        access_token=token,
        username=str(user.username),
        full_name=str(user.full_name),
        role=str(user.role),
        email=str(user.email),
    )


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    return current_user
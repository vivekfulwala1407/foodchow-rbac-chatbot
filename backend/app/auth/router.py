from fastapi import APIRouter, HTTPException, status, Depends

from app.auth.schemas import LoginRequest, LoginResponse, CurrentUser
from app.auth.service import authenticate_user, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    - Verifies username + password
    - Returns a signed JWT token valid for JWT_EXPIRE_HOURS
    - Frontend stores this token and sends it with every future request
    """
    user = authenticate_user(request.username, request.password)

    if not user:
        # Always return the same vague message — never say "wrong password"
        # vs "user not found" — that leaks which usernames exist
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token(
        username=user["username"],
        role=user["role"],
    )

    return LoginResponse(
        access_token=token,
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        email=user["email"],
    )


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Returns the currently logged-in user's info.
    Requires a valid JWT token in the Authorization header.
    Frontend uses this to verify the token is still valid on page refresh.
    """
    return current_user
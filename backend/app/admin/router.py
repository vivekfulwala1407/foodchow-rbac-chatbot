import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.auth.service import hash_password
from app.database.connection import get_db
from app.database.models import User
from app.admin.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    ResetPasswordRequest,
    UserResponse,
    UsersListResponse,
)

router = APIRouter(prefix="/admin", tags=["Admin"])

VALID_ROLES = [
    "finance", "marketing", "hr",
    "engineering", "employee", "c_level"
]


def require_super_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required.",
        )
    return current_user


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        user_id=str(user.user_id),
        username=str(user.username),
        full_name=str(user.full_name),
        email=str(user.email),
        role=str(user.role),
        is_active=bool(user.is_active),
        created_at=str(user.created_at) if user.created_at else None,
        created_by=str(user.created_by) if user.created_by else None,
    )


@router.get("/users", response_model=UsersListResponse)
def list_users(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_super_admin),
):
    users = db.query(User).filter(
        User.role != "super_admin"
    ).order_by(User.created_at.desc()).all()

    return UsersListResponse(
        users=[user_to_response(u) for u in users],
        total=len(users),
    )


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_super_admin),
):
    if request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already exists.")

    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already exists.")

    new_user = User(
        user_id=str(uuid.uuid4()),
        username=request.username,
        password_hash=hash_password(request.password),
        role=request.role,
        full_name=request.full_name,
        email=request.email,
        is_active=True,
        created_by=current_user.username,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return user_to_response(new_user)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_super_admin),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if request.role and request.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role.")

    if request.full_name:
        user.full_name = request.full_name  # type: ignore[assignment]
    if request.email:
        user.email = request.email  # type: ignore[assignment]
    if request.role:
        user.role = request.role  # type: ignore[assignment]
    if request.is_active is not None:
        user.is_active = request.is_active  # type: ignore[assignment]

    db.commit()
    db.refresh(user)
    return user_to_response(user)


@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: str,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_super_admin),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.password_hash = hash_password(request.new_password)  # type: ignore[assignment]
    db.commit()
    return {"message": f"Password reset successfully for {user.username}"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_super_admin),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted successfully."}
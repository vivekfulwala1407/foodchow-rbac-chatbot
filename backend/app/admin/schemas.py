from pydantic import BaseModel
from typing import Optional


class CreateUserRequest(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    role: str


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    new_password: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    created_by: Optional[str] = None


class UsersListResponse(BaseModel):
    users: list[UserResponse]
    total: int
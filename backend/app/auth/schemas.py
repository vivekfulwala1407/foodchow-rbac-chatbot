from pydantic import BaseModel
from typing import Optional


# What the user sends to /auth/login
class LoginRequest(BaseModel):
    username: str
    password: str


# What we send back after successful login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str
    role: str
    email: str


# What lives inside the JWT token (the decoded payload)
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# Current logged-in user info (used across the app)
class CurrentUser(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: str
    email: str
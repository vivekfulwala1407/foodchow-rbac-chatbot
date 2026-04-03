from fastapi import HTTPException, status
from app.auth.schemas import CurrentUser

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "super_admin": [],
    "c_level": ["finance", "marketing", "hr", "engineering", "general"],
    "finance": ["finance", "general"],
    "marketing": ["marketing", "general"],
    "hr": ["hr", "general"],
    "engineering": ["engineering", "general"],
    "employee": ["general"],
}

ROLE_DISPLAY_NAMES: dict[str, str] = {
    "super_admin": "Super Administrator",
    "c_level": "C-Level Executive",
    "finance": "Finance Team",
    "marketing": "Marketing Team",
    "hr": "HR Team",
    "engineering": "Engineering Department",
    "employee": "Employee",
}


def get_allowed_departments(role: str) -> list[str]:
    if role == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin does not have chat access. Use the admin panel.",
        )
    allowed = ROLE_PERMISSIONS.get(role)
    if allowed is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Unknown role '{role}'. Access denied.",
        )
    return allowed


def verify_access(current_user: CurrentUser) -> list[str]:
    return get_allowed_departments(current_user.role)


def get_role_display_name(role: str) -> str:
    return ROLE_DISPLAY_NAMES.get(role, role.title())
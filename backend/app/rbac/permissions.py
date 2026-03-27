from fastapi import HTTPException, status
from app.auth.schemas import CurrentUser


# Master mapping — Role → which document departments they can access
# This is the single source of truth for all access control in the system
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "c_level": [
        "finance",
        "marketing",
        "hr",
        "engineering",
        "general",
    ],
    "finance": [
        "finance",
        "general",
    ],
    "marketing": [
        "marketing",
        "general",
    ],
    "hr": [
        "hr",
        "general",
    ],
    "engineering": [
        "engineering",
        "general",
    ],
    "employee": [
        "general",
    ],
}

# Human-readable role display names (used in UI responses)
ROLE_DISPLAY_NAMES: dict[str, str] = {
    "c_level": "C-Level Executive",
    "finance": "Finance Team",
    "marketing": "Marketing Team",
    "hr": "HR Team",
    "engineering": "Engineering Department",
    "employee": "Employee",
}


def get_allowed_departments(role: str) -> list[str]:
    """
    Returns the list of document departments a role can access.

    Why we filter at retrieval time:
    - If we fetched all docs and filtered after, restricted data
      would briefly exist in memory — a security risk.
    - Filtering at the DB query level means restricted data is
      never touched at all.
    """
    allowed = ROLE_PERMISSIONS.get(role)

    if allowed is None:
        # Unknown role — deny everything, log-worthy event
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Unknown role '{role}'. Access denied.",
        )

    return allowed


def verify_access(current_user: CurrentUser) -> list[str]:
    """
    Validates user's role and returns their allowed departments.
    This is the function called at the start of every chat query.

    Returns the list of allowed departments for use in vector DB filter.
    """
    allowed_departments = get_allowed_departments(current_user.role)
    return allowed_departments


def get_role_display_name(role: str) -> str:
    """Returns a human-friendly role name for display in responses."""
    return ROLE_DISPLAY_NAMES.get(role, role.title())
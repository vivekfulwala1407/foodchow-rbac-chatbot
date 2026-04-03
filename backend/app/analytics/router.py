from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.analytics.schemas import AnalyticsResponse
from app.analytics.service import get_analytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def analytics(current_user: CurrentUser = Depends(get_current_user)):
    """
    Returns analytics data from audit logs.

    Why restrict to c_level only?
    Query history contains sensitive info about who
    accessed what — only executives should see this.
    All other roles get a 403.
    """
    from fastapi import HTTPException, status

    if current_user.role != "c_level":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics dashboard is restricted to C-Level executives only.",
        )

    return get_analytics()
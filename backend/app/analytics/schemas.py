from pydantic import BaseModel


class RoleStats(BaseModel):
    role: str
    query_count: int
    percentage: float


class DocumentStats(BaseModel):
    document: str
    access_count: int
    department: str


class DailyStats(BaseModel):
    date: str
    query_count: int


class RecentQuery(BaseModel):
    timestamp: str
    username: str
    role: str
    query: str
    sources_used: list[str]
    chunks_found: int
    status: str


class AnalyticsSummary(BaseModel):
    total_queries: int
    total_users: int
    most_active_role: str
    most_accessed_document: str
    success_rate: float


class AnalyticsResponse(BaseModel):
    summary: AnalyticsSummary
    queries_by_role: list[RoleStats]
    top_documents: list[DocumentStats]
    daily_activity: list[DailyStats]
    recent_queries: list[RecentQuery]
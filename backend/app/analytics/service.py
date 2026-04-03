import json
import os
from collections import defaultdict
from datetime import datetime, timezone

from app.analytics.schemas import (
    AnalyticsResponse,
    AnalyticsSummary,
    DailyStats,
    DocumentStats,
    RecentQuery,
    RoleStats,
)

LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "logs",
    "audit.log",
)

# Maps department label to document category
DEPARTMENT_MAP = {
    "finance": "Finance",
    "marketing": "Marketing",
    "hr": "HR",
    "engineering": "Engineering",
    "general": "General",
}


def read_logs() -> list[dict]:
    """Reads all log entries from audit.log."""
    if not os.path.exists(LOG_FILE):
        return []

    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def get_analytics() -> AnalyticsResponse:
    """
    Reads audit.log and computes analytics stats.

    This runs on every /analytics request.
    For large scale, you'd cache this or use a real DB.
    For this project, reading the log file is perfectly fine.
    """
    logs = read_logs()

    # Filter only query logs (not auth failures)
    query_logs = [
        l for l in logs
        if l.get("status") in ("success", "error")
        and "query" in l
    ]

    if not query_logs:
        return _empty_response()

    # ── Queries by role ──────────────────────────────────────────────
    role_counts: dict[str, int] = defaultdict(int)
    for log in query_logs:
        role_counts[log.get("role", "unknown")] += 1

    total_queries = len(query_logs)
    queries_by_role = [
        RoleStats(
            role=role,
            query_count=count,
            percentage=round((count / total_queries) * 100, 1),
        )
        for role, count in sorted(
            role_counts.items(), key=lambda x: x[1], reverse=True
        )
    ]

    # ── Top documents ────────────────────────────────────────────────
    doc_counts: dict[str, int] = defaultdict(int)
    for log in query_logs:
        for source in log.get("sources_used", []):
            doc_counts[source] += 1

    top_documents = []
    for doc, count in sorted(
        doc_counts.items(), key=lambda x: x[1], reverse=True
    )[:8]:
        # Infer department from filename
        dept = "General"
        for key in DEPARTMENT_MAP:
            if key in doc.lower():
                dept = DEPARTMENT_MAP[key]
                break
        top_documents.append(
            DocumentStats(
                document=doc,
                access_count=count,
                department=dept,
            )
        )

    # ── Daily activity ───────────────────────────────────────────────
    daily_counts: dict[str, int] = defaultdict(int)
    for log in query_logs:
        try:
            date_str = log["timestamp"][:10]  # YYYY-MM-DD
            daily_counts[date_str] += 1
        except (KeyError, IndexError):
            continue

    daily_activity = [
        DailyStats(date=date, query_count=count)
        for date, count in sorted(daily_counts.items())[-14:]  # last 14 days
    ]

    # ── Recent queries ───────────────────────────────────────────────
    recent_queries = []
    for log in reversed(query_logs[-20:]):
        recent_queries.append(
            RecentQuery(
                timestamp=log.get("timestamp", ""),
                username=log.get("username", ""),
                role=log.get("role", ""),
                query=log.get("query", ""),
                sources_used=log.get("sources_used", []),
                chunks_found=log.get("chunks_found", 0),
                status=log.get("status", ""),
            )
        )

    # ── Summary ──────────────────────────────────────────────────────
    unique_users = len({l.get("username") for l in query_logs})
    most_active_role = queries_by_role[0].role if queries_by_role else "N/A"
    most_accessed_doc = top_documents[0].document if top_documents else "N/A"
    success_count = sum(
        1 for l in query_logs if l.get("status") == "success"
    )
    success_rate = round((success_count / total_queries) * 100, 1)

    summary = AnalyticsSummary(
        total_queries=total_queries,
        total_users=unique_users,
        most_active_role=most_active_role,
        most_accessed_document=most_accessed_doc,
        success_rate=success_rate,
    )

    return AnalyticsResponse(
        summary=summary,
        queries_by_role=queries_by_role,
        top_documents=top_documents,
        daily_activity=daily_activity,
        recent_queries=recent_queries,
    )


def _empty_response() -> AnalyticsResponse:
    """Returns empty analytics when no logs exist yet."""
    return AnalyticsResponse(
        summary=AnalyticsSummary(
            total_queries=0,
            total_users=0,
            most_active_role="N/A",
            most_accessed_document="N/A",
            success_rate=0.0,
        ),
        queries_by_role=[],
        top_documents=[],
        daily_activity=[],
        recent_queries=[],
    )
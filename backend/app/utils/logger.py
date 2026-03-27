import json
import os
from datetime import datetime, timezone


LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "audit.log")


def log_query(
    username: str,
    role: str,
    query: str,
    sources: list[str],
    chunks_found: int,
    status: str = "success",
) -> None:
    """
    Writes every query to audit.log as a JSON line.

    Why audit logging?
    - Security requirement — track who accessed what
    - Debugging — trace exactly what was retrieved
    - Compliance — financial companies need access trails
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "role": role,
        "query": query,
        "sources_used": sources,
        "chunks_found": chunks_found,
        "status": status,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_auth_failure(username: str, reason: str) -> None:
    """Logs failed authentication attempts."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "status": "auth_failed",
        "reason": reason,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
"""Token usage tracking and persistence."""
import json
import sqlite3
import threading
from datetime import datetime, date
from typing import Optional

from config import DB_PATH, PRICING


class UsageTracker:
    """Tracks DeepSeek token usage with SQLite persistence."""

    def __init__(self):
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self._init_db()
        # In-memory session counters
        self._session_tokens = {"prompt": 0, "completion": 0, "total": 0}
        self._session_cost = 0.0
        self._last_usage = None

    def _init_db(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_log(timestamp)
        """)
        self._conn.commit()

    def record_usage(self, prompt_tokens: int, completion_tokens: int,
                     model: str = "default"):
        """Record a token usage event."""
        total = prompt_tokens + completion_tokens
        pricing = PRICING.get(model, PRICING["default"])
        cost = (prompt_tokens / 1_000_000 * pricing["input"] +
                completion_tokens / 1_000_000 * pricing["output"])

        now = datetime.now().isoformat()

        with self._lock:
            self._conn.execute(
                "INSERT INTO usage_log (timestamp, model, prompt_tokens, completion_tokens, total_tokens, cost) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (now, model, prompt_tokens, completion_tokens, total, cost),
            )
            self._conn.commit()

            self._session_tokens["prompt"] += prompt_tokens
            self._session_tokens["completion"] += completion_tokens
            self._session_tokens["total"] += total
            self._session_cost += cost
            self._last_usage = {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": total,
                "cost": cost,
                "model": model,
                "timestamp": now,
            }

    def get_today_usage(self) -> dict:
        """Get aggregated usage for today."""
        today = date.today().isoformat()
        with self._lock:
            row = self._conn.execute(
                "SELECT COALESCE(SUM(prompt_tokens),0), COALESCE(SUM(completion_tokens),0), "
                "COALESCE(SUM(total_tokens),0), COALESCE(SUM(cost),0) "
                "FROM usage_log WHERE timestamp >= ?",
                (today,),
            ).fetchone()
        return {
            "prompt": row[0],
            "completion": row[1],
            "total": row[2],
            "cost": round(row[3], 6),
        }

    def get_session_usage(self) -> dict:
        """Get current session usage (in-memory)."""
        with self._lock:
            return dict(self._session_tokens)

    def get_session_cost(self) -> float:
        with self._lock:
            return self._session_cost

    def get_last_usage(self) -> Optional[dict]:
        with self._lock:
            return self._last_usage

    def get_all_time_usage(self) -> dict:
        """Get all-time aggregated usage."""
        with self._lock:
            row = self._conn.execute(
                "SELECT COALESCE(SUM(prompt_tokens),0), COALESCE(SUM(completion_tokens),0), "
                "COALESCE(SUM(total_tokens),0), COALESCE(SUM(cost),0) FROM usage_log",
            ).fetchone()
        return {
            "prompt": row[0],
            "completion": row[1],
            "total": row[2],
            "cost": round(row[3], 6),
        }

    def get_recent_requests(self, limit: int = 20) -> list:
        """Get most recent requests."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT timestamp, model, prompt_tokens, completion_tokens, total_tokens, cost "
                "FROM usage_log ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "timestamp": r[0],
                "model": r[1],
                "prompt": r[2],
                "completion": r[3],
                "total": r[4],
                "cost": r[5],
            }
            for r in rows
        ]

    def reset_session(self):
        """Reset session counters."""
        with self._lock:
            self._session_tokens = {"prompt": 0, "completion": 0, "total": 0}
            self._session_cost = 0.0
            self._last_usage = None


# Global singleton
_tracker = None


def get_tracker() -> UsageTracker:
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker

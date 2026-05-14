"""Token usage tracker - reads directly from CC-Switch database."""
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from config import PRICING


CC_SWITCH_DB = str(Path.home() / ".cc-switch" / "cc-switch.db")
DEEPSEEK_PROVIDER_ID = "bb3cb8ec-eacc-4e7c-bbc6-fdadbeb231c7"


class UsageTracker:
    """Reads token usage from CC-Switch's proxy_request_logs."""

    def __init__(self):
        self._lock = threading.Lock()
        self._session_start = int(time.time())
        self._last_usage = None
        self._request_count = 0
        self._last_status = "no requests yet"

    def _query(self, sql, params=()):
        conn = sqlite3.connect(CC_SWITCH_DB)
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def _midnight_ts(self) -> int:
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return int(today.timestamp())

    @staticmethod
    def _calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
        pricing = PRICING.get("default", {"input": 0.27, "output": 1.10})
        return (prompt_tokens / 1_000_000 * pricing["input"] +
                completion_tokens / 1_000_000 * pricing["output"])

    def get_today_usage(self) -> dict:
        ts = self._midnight_ts()
        rows = self._query("""
            SELECT COALESCE(SUM(input_tokens),0), COALESCE(SUM(output_tokens),0)
            FROM proxy_request_logs
            WHERE provider_id = ? AND created_at >= ?
        """, (DEEPSEEK_PROVIDER_ID, ts))
        prompt = rows[0][0]
        completion = rows[0][1]
        total = prompt + completion
        cost = self._calculate_cost(prompt, completion)
        return {"prompt": prompt, "completion": completion, "total": total, "cost": round(cost, 6)}

    def get_session_usage(self) -> dict:
        rows = self._query("""
            SELECT COALESCE(SUM(input_tokens),0), COALESCE(SUM(output_tokens),0)
            FROM proxy_request_logs
            WHERE provider_id = ? AND created_at >= ?
        """, (DEEPSEEK_PROVIDER_ID, self._session_start))
        prompt = rows[0][0]
        completion = rows[0][1]
        return {"prompt": prompt, "completion": completion, "total": prompt + completion}

    def get_session_cost(self) -> float:
        usage = self.get_session_usage()
        return self._calculate_cost(usage["prompt"], usage["completion"])

    def get_last_usage(self) -> dict | None:
        rows = self._query("""
            SELECT input_tokens, output_tokens, model, created_at
            FROM proxy_request_logs
            WHERE provider_id = ? AND data_source = 'proxy'
            ORDER BY created_at DESC LIMIT 1
        """, (DEEPSEEK_PROVIDER_ID,))
        if not rows:
            return None
        prompt, completion, model, ts = rows[0]
        cost = self._calculate_cost(prompt, completion)
        return {
            "prompt": prompt,
            "completion": completion,
            "total": prompt + completion,
            "cost": round(cost, 6),
            "model": model or "deepseek",
            "timestamp": str(ts),
        }

    def get_request_count(self) -> int:
        rows = self._query("""
            SELECT COUNT(*) FROM proxy_request_logs
            WHERE provider_id = ? AND data_source = 'proxy'
        """, (DEEPSEEK_PROVIDER_ID,))
        return rows[0][0] if rows else 0

    def get_last_status(self) -> str:
        rows = self._query("""
            SELECT status_code, error_message
            FROM proxy_request_logs
            WHERE provider_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (DEEPSEEK_PROVIDER_ID,))
        if not rows:
            return "no requests yet"
        code, err = rows[0]
        if err:
            return f"HTTP {code}: {err[:30]}"
        return f"HTTP {code}"

    def get_recent_requests(self, limit=10) -> list:
        rows = self._query("""
            SELECT created_at, model, input_tokens, output_tokens, status_code
            FROM proxy_request_logs
            WHERE provider_id = ? AND data_source = 'proxy'
            ORDER BY created_at DESC LIMIT ?
        """, (DEEPSEEK_PROVIDER_ID, limit))
        return [
            {
                "timestamp": r[0],
                "model": r[1],
                "prompt": r[2],
                "completion": r[3],
                "status": r[4],
            }
            for r in rows
        ]


_tracker = None


def get_tracker() -> UsageTracker:
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker

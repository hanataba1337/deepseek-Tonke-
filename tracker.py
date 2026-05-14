"""Token usage tracker - reads directly from CC-Switch database."""
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from config import PRICING, MODEL_LABELS

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
    def _cost(prompt: int, completion: int, model: str = "default") -> float:
        pricing = PRICING.get(model, PRICING["default"])
        return (prompt / 1_000_000 * pricing["input"] +
                completion / 1_000_000 * pricing["output"])

    def get_today_usage(self) -> dict:
        # Sum per-model costs for accurate pricing
        breakdown = self.get_model_breakdown()
        prompt = sum(m["prompt"] for m in breakdown)
        completion = sum(m["completion"] for m in breakdown)
        cost = sum(m["cost"] for m in breakdown)
        return {"prompt": prompt, "completion": completion,
                "total": prompt + completion, "cost": round(cost, 6)}

    def get_model_breakdown(self) -> list:
        """Get today's usage grouped by model."""
        ts = self._midnight_ts()
        rows = self._query("""
            SELECT COALESCE(model,'unknown'), COALESCE(SUM(input_tokens),0),
                   COALESCE(SUM(output_tokens),0)
            FROM proxy_request_logs
            WHERE provider_id = ? AND created_at >= ?
            GROUP BY model
            ORDER BY SUM(input_tokens + output_tokens) DESC
        """, (DEEPSEEK_PROVIDER_ID, ts))
        result = []
        for r in rows:
            m, pin, pout = r
            label = MODEL_LABELS.get(m, m) if m else "unknown"
            cost = round(self._cost(pin, pout, m), 6)
            result.append({"model": m, "label": label,
                           "prompt": pin, "completion": pout,
                           "total": pin + pout, "cost": cost})
        return result

    def get_active_models(self) -> list:
        """List models used today with their prompts/outputs."""
        ts = self._midnight_ts()
        rows = self._query("""
            SELECT COALESCE(model,'unknown'), COUNT(*)
            FROM proxy_request_logs
            WHERE provider_id = ? AND created_at >= ? AND data_source = 'proxy'
            GROUP BY model
            ORDER BY COUNT(*) DESC
        """, (DEEPSEEK_PROVIDER_ID, ts))
        return [{"model": r[0], "label": MODEL_LABELS.get(r[0], r[0]), "count": r[1]} for r in rows]

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
        return self._cost(usage["prompt"], usage["completion"])

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
        m = model or "default"
        return {
            "prompt": prompt, "completion": completion,
            "total": prompt + completion,
            "cost": round(self._cost(prompt, completion, m), 6),
            "model": model or "deepseek",
            "label": MODEL_LABELS.get(m, m),
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
        return [{"timestamp": r[0], "model": r[1], "label": MODEL_LABELS.get(r[1] or "", r[1] or ""),
                 "prompt": r[2], "completion": r[3], "status": r[4]} for r in rows]


_tracker = None


def get_tracker() -> UsageTracker:
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker

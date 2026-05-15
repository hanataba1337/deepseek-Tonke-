"""Fetch usage data from DeepSeek official API."""
import json
import time
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError

from settings import get as get_setting

BASE = "https://api.deepseek.com"

_TZ = timezone(timedelta(hours=8))


def _api_key() -> str:
    return (get_setting("api_key") or "").strip()


def _today_range() -> tuple[str, str]:
    """Return (start_date, end_date) for today in Beijing time (YYYY-MM-DD)."""
    today = datetime.now(_TZ)
    return today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")


def _month_range() -> tuple[str, str]:
    """Return (start_date, end_date) for this month."""
    now = datetime.now(_TZ)
    start = now.replace(day=1).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    return start, end


def _get(path: str) -> dict | None:
    key = _api_key()
    if not key:
        return None
    try:
        req = Request(f"{BASE}{path}", headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        })
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except (URLError, OSError, json.JSONDecodeError) as e:
        return None


def get_today_cost() -> float | None:
    """Get today's total cost in RMB via DeepSeek billing API."""
    start, end = _today_range()
    data = _get(f"/v1/dashboard/billing/usage?start_date={start}&end_date={end}")
    if data is None:
        return None
    # Returns {"object":"list","total_usage":0.0,"data":[...]}
    # total_usage is in USD (like OpenAI format)
    total_usd = data.get("total_usage", 0.0)
    return round(total_usd * 7.2, 6)  # USD → RMB


def get_monthly_cost() -> float | None:
    """Get this month's total cost via DeepSeek billing API."""
    start, end = _month_range()
    data = _get(f"/v1/dashboard/billing/usage?start_date={start}&end_date={end}")
    if data is None:
        return None
    total_usd = data.get("total_usage", 0.0)
    return round(total_usd * 7.2, 6)


def get_balance() -> float | None:
    """Get remaining balance in RMB."""
    data = _get("/user/balance")
    if data is None:
        return None
    # Returns {"balance": "0.00", "total_balance": "0.00"} (in RMB)
    balance = data.get("balance", 0)
    return round(float(balance), 2)


def available() -> bool:
    """Check if API key is configured and usable."""
    return bool(_api_key())

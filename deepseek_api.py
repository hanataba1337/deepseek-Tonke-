"""Fetch balance from DeepSeek official API — primary data source."""
import json
import time
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from settings import get as get_setting, save as save_setting

BASE = "https://api.deepseek.com"
_TZ = timezone(timedelta(hours=8))

_last_error: str | None = None


def last_error() -> str | None:
    return _last_error


def _api_key() -> str:
    return (get_setting("api_key") or "").strip()


def _get(path: str) -> dict | None:
    global _last_error
    key = _api_key()
    if not key:
        _last_error = None
        return None
    try:
        req = Request(f"{BASE}{path}", headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        })
        with urlopen(req, timeout=10) as resp:
            _last_error = None
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode(errors="replace")[:100]
        _last_error = f"HTTP {e.code}: {body}"
        return None
    except (URLError, OSError, ValueError) as e:
        _last_error = str(e)
        return None


def get_balance() -> float | None:
    data = _get("/user/balance")
    if data is None:
        return None
    infos = data.get("balance_infos", [])
    total = sum(float(x.get("total_balance", 0)) for x in infos)
    return round(total, 2)


def available() -> bool:
    key = _api_key()
    if not key:
        return False
    bal = get_balance()
    return bal is not None


def verify() -> str:
    key = _api_key()
    if not key:
        return "no key"
    bal = get_balance()
    if bal is not None:
        return f"OK (¥{bal})"
    return f"error: {_last_error}" if _last_error else "error"


# ── Balance snapshot tracking ──────────────────────────────────

def _today_str() -> str:
    return datetime.now(_TZ).strftime("%Y-%m-%d")


def _month_str() -> str:
    return datetime.now(_TZ).strftime("%Y-%m")


def load_snapshots() -> dict:
    raw = get_setting("_bs") or {}
    return raw if isinstance(raw, dict) else {}


def save_snapshot(balance: float):
    """Store current balance as the latest snapshot for today and this month."""
    snaps = load_snapshots()
    today = _today_str()
    month = _month_str()
    now = time.time()
    # Update today's snapshot (keep earliest of today as the baseline)
    if today not in snaps:
        snaps[today] = {"bal": balance, "ts": now}
    else:
        # Also store the latest reading for live comparison
        snaps[today + "_latest"] = {"bal": balance, "ts": now}
    # Monthly
    if month not in snaps:
        snaps[month] = {"bal": balance, "ts": now}
    else:
        snaps[month + "_latest"] = {"bal": balance, "ts": now}
    save_setting({"_bs": snaps})


def get_today_cost(current_balance: float) -> float:
    """Return today's actual spending based on balance snapshots."""
    snaps = load_snapshots()
    today = _today_str()
    entry = snaps.get(today)
    if entry is None:
        return 0.0
    spent = entry["bal"] - current_balance
    return round(max(0, spent), 4)


def get_month_cost(current_balance: float) -> float:
    """Return this month's actual spending based on balance snapshots."""
    snaps = load_snapshots()
    month = _month_str()
    entry = snaps.get(month)
    if entry is None:
        return 0.0
    spent = entry["bal"] - current_balance
    return round(max(0, spent), 4)

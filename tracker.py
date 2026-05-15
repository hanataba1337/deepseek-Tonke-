"""Usage tracker — reads from DeepSeek API (balance tracking)."""
from deepseek_api import (
    get_balance, available, last_error, verify,
    save_snapshot, get_today_cost, get_month_cost,
)


class UsageTracker:
    def __init__(self):
        self._balance: float | None = None
        self._today_cost: float = 0.0
        self._month_cost: float = 0.0
        self._prev_balance: float | None = None
        self._session_spent: float = 0.0  # balance drops within this session
        self._refresh_balance()

    def _refresh_balance(self):
        bal = get_balance()
        if bal is None:
            return
        self._prev_balance = self._balance
        self._balance = bal

        # Track session spending from balance drops
        if self._prev_balance is not None and bal < self._prev_balance:
            self._session_spent += self._prev_balance - bal

        # Update snapshots
        save_snapshot(bal)

        # Get costs from snapshot comparison
        self._today_cost = get_today_cost(bal)
        self._month_cost = get_month_cost(bal)

    def update(self):
        """Call every refresh cycle to track balance changes."""
        self._refresh_balance()

    def data_source(self) -> str:
        if self._balance is not None:
            return f"API ¥{self._balance}"
        err = last_error()
        return f"API error" if err else "no key"

    def ok(self) -> bool:
        return self._balance is not None

    def get_today_usage(self) -> dict:
        return {"cost": self._today_cost}

    def get_monthly_cost(self) -> float:
        return self._month_cost

    def get_balance(self) -> float | None:
        return self._balance

    def get_session_spent(self) -> float:
        return round(self._session_spent, 4)

    def last_api_error(self) -> str | None:
        return last_error()

    def verify(self) -> str:
        return verify()


_tracker = None


def get_tracker() -> UsageTracker:
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker

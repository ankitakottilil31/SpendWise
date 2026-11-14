"""Single monthly budget setting."""
import math
import sqlite3


class SettingsService:
    """Persist the monthly spending target."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_budget(self) -> float:
        """Return the saved monthly target."""
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", ("monthly_budget",)).fetchone()
        return float(row[0]) if row else 30000.0

    def set_budget(self, value: str | float) -> None:
        """Validate and store a positive finite budget."""
        try:
            budget = float(str(value).replace(",", "").strip())
        except (TypeError, ValueError) as exc:
            raise ValueError("Enter a valid budget amount.") from exc
        if not math.isfinite(budget) or budget <= 0:
            raise ValueError("Budget must be greater than zero.")
        self.conn.execute(
            "INSERT INTO settings(key,value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("monthly_budget", str(budget)),
        )
        self.conn.commit()

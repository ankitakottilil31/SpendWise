"""Expense validation, CRUD, filtering and dashboard calculations."""
from datetime import date
import math
import sqlite3


class ExpenseService:
    """Own all business rules for expense entries."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def validate(self, amount: str | float, category_id: int | str, day: str) -> dict[str, str]:
        """Return field-specific validation errors for an expense."""
        errors = {}
        try:
            number = float(str(amount).replace(",", "").strip())
            if not math.isfinite(number) or number <= 0:
                errors["amount"] = "Amount must be greater than zero."
        except (TypeError, ValueError):
            errors["amount"] = "Enter a valid positive number."
        try:
            parsed = date.fromisoformat(str(day))
            if parsed.isoformat() != str(day):
                raise ValueError
        except (TypeError, ValueError):
            errors["date"] = "Choose a valid date (YYYY-MM-DD)."
        try:
            row = self.conn.execute("SELECT id FROM categories WHERE id=?", (int(category_id),)).fetchone()
            if row is None:
                errors["category"] = "Choose a category."
        except (TypeError, ValueError):
            errors["category"] = "Choose a category."
        return errors

    def save(self, amount: str | float, category_id: int | str, day: str,
             note: str = "", expense_id: int | None = None) -> int:
        """Insert or update an expense after validating fields."""
        errors = self.validate(amount, category_id, day)
        if errors:
            raise ValueError(next(iter(errors.values())))
        if expense_id is None:
            cursor = self.conn.execute(
                "INSERT INTO expenses(amount,category_id,date,note) VALUES (?,?,?,?)",
                (float(str(amount).replace(",", "")), int(category_id), day, (note or "").strip()),
            )
            result = cursor.lastrowid
        else:
            cursor = self.conn.execute(
                "UPDATE expenses SET amount=?,category_id=?,date=?,note=? WHERE id=?",
                (float(str(amount).replace(",", "")), int(category_id), day, (note or "").strip(), expense_id),
            )
            if not cursor.rowcount:
                raise ValueError("Expense not found.")
            result = expense_id
        self.conn.commit()
        return int(result)

    def delete(self, expense_id: int) -> None:
        """Delete one selected expense."""
        cursor = self.conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        if not cursor.rowcount:
            raise ValueError("Expense not found.")
        self.conn.commit()

    def get(self, expense_id: int) -> dict | None:
        """Retrieve one expense for the edit form."""
        row = self.conn.execute("SELECT * FROM expenses WHERE id=?", (expense_id,)).fetchone()
        return dict(row) if row else None

    def list_all(self, search: str = "", category_id: int | None = None,
                 month: str = "") -> list[dict]:
        """Return filtered entries with category names, newest first."""
        sql = ("SELECT e.id,e.amount,e.category_id,e.date,e.note,c.name AS category "
               "FROM expenses e JOIN categories c ON c.id=e.category_id WHERE 1=1")
        args: list = []
        if search:
            sql += " AND LOWER(COALESCE(e.note,'')) LIKE ?"
            args.append("%" + search.lower() + "%")
        if category_id is not None:
            sql += " AND e.category_id=?"
            args.append(category_id)
        if month:
            sql += " AND substr(e.date,1,7)=?"
            args.append(month)
        sql += " ORDER BY e.date DESC,e.id DESC"
        return [dict(row) for row in self.conn.execute(sql, args).fetchall()]

    def months(self) -> list[str]:
        """List available months newest first."""
        rows = self.conn.execute("SELECT DISTINCT substr(date,1,7) AS month FROM expenses ORDER BY month DESC")
        return [row[0] for row in rows]

    def summary(self) -> dict:
        """Return overall, current-month and leading-category spending."""
        current = date.today().strftime("%Y-%m")
        total = self.conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()[0]
        monthly = self.conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE substr(date,1,7)=?", (current,)
        ).fetchone()[0]
        rows = self.category_totals()
        top = max(rows, key=lambda item: item["total"])['category'] if rows else "—"
        return {"total": total, "month": monthly, "top_category": top}

    def category_totals(self) -> list[dict]:
        """Group all expenses by category for the donut chart."""
        sql = ("SELECT c.name AS category,SUM(e.amount) AS total FROM expenses e "
               "JOIN categories c ON c.id=e.category_id GROUP BY c.id ORDER BY total DESC")
        return [dict(row) for row in self.conn.execute(sql)]

"""Rules for managing expense categories."""
import sqlite3


class CategoryService:
    """Read and maintain categories without exposing SQL to the UI."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_all(self) -> list[dict]:
        """Return categories alphabetically."""
        rows = self.conn.execute("SELECT id,name FROM categories ORDER BY name").fetchall()
        return [dict(row) for row in rows]

    def add(self, name: str) -> None:
        """Save a unique, nonempty category name."""
        name = (name or "").strip()
        if not name:
            raise ValueError("Enter a category name.")
        if len(name) > 40:
            raise ValueError("Category name must be 40 characters or fewer.")
        try:
            self.conn.execute("INSERT INTO categories(name) VALUES (?)", (name,))
            self.conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("That category already exists.") from exc

    def delete(self, category_id: int) -> None:
        """Prevent deleting categories with linked expenses."""
        count = self.conn.execute(
            "SELECT COUNT(*) FROM expenses WHERE category_id=?", (category_id,)
        ).fetchone()[0]
        if count:
            raise ValueError("This category has expenses. Delete or reassign them first.")
        cursor = self.conn.execute("DELETE FROM categories WHERE id=?", (category_id,))
        if not cursor.rowcount:
            raise ValueError("Category not found.")
        self.conn.commit()

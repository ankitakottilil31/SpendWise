"""Database connection and initial demo data."""
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "spendwise.db"
CATEGORIES = ("Food", "Transport", "Rent", "Shopping", "Bills", "Health", "Entertainment", "Other")


def connect(path: str | Path = DEFAULT_PATH) -> sqlite3.Connection:
    """Open a connection with named columns and enforced foreign keys."""
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    """Create the three tables and seed a fresh database only."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL CHECK(amount > 0),
            category_id INTEGER NOT NULL REFERENCES categories(id),
            date TEXT NOT NULL, note TEXT
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT NOT NULL
        );
    """)
    fresh = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0
    if fresh:
        conn.executemany("INSERT INTO categories(name) VALUES (?)", [(n,) for n in CATEGORIES])
    conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES (?,?)", ("monthly_budget", "30000"))
    if fresh and conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 0:
        seed_expenses(conn)
    conn.commit()


def seed_expenses(conn: sqlite3.Connection) -> None:
    """Add 40 deterministic, dated example purchases over three months."""
    choices = [
        (240, "Lunch"), (85, "Bus fare"), (11500, "Room rent"),
        (670, "Groceries"), (899, "Phone bill"), (320, "Pharmacy"),
        (450, "Movie"), (199, "Stationery"), (160, "Coffee"),
        (540, "Household supplies"),
    ]
    today = date.today()
    for i in range(40):
        amount, note = choices[i % len(choices)]
        # Spread entries through the current and preceding two calendar months.
        month_offset = i % 3
        year = today.year
        month = today.month - month_offset
        while month < 1:
            year, month = year - 1, month + 12
        last_day = __import__('calendar').monthrange(year, month)[1]
        day = min(1 + (i * 7) % 27, last_day)
        if month_offset == 0:
            day = min(day, today.day)
        d = date(year, month, day).isoformat()
        conn.execute(
            "INSERT INTO expenses(amount,category_id,date,note) VALUES (?,?,?,?)",
            (amount + (i % 4) * 25, i % 8 + 1, d, note),
        )

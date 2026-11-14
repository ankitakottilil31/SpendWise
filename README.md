# 💸 SpendWise — Expense Tracker

SpendWise is a desktop expense tracker built for a university Python project. It uses a tkinter interface, ttkbootstrap themes, a single embedded Matplotlib donut chart, and a local SQLite database. It opens with 40 example transactions so the dashboard can be demonstrated immediately.

## Features

- Dashboard: total spent, spending this month, top category, color-coded monthly budget Meter, one category donut chart, and five newest transactions.
- Transactions: search note text, filter by category and month, add/edit/delete entries with confirmation for deletion, and export the current filtered view to CSV.
- Add/Edit expense: amount, category, date picker, and note, with inline validation messages.
- Categories: create and delete custom categories; categories in use cannot be deleted.
- Monthly budget: saved numeric target, initially ₹30,000, editable from the dashboard.
- Built-in flatly light and darkly dark themes with a toggle; chart colors refresh on switch.
- Non-blocking success toasts, persistent SQLite storage, and in-memory automated tests.

## Setup and run

Requires **Python 3.10+** and tkinter support (usually bundled with Python; on some Linux installations install your distribution's `python3-tk` package). Open a terminal **inside the `spendwise` directory**.

```text
python -m venv venv
venv\Scripts\activate   (Windows)  |  source venv/bin/activate  (macOS/Linux)
pip install -r requirements.txt
python main.py
```

The activation commands above are alternatives; run only the one for your OS. On Windows PowerShell, use `venv\Scripts\Activate.ps1` instead. If `python` is missing on macOS/Linux, use `python3`.

**Run tests:**

```text
python -m unittest discover tests
```

**GUI smoke check:**

```text
python main.py --check
```

The smoke check creates the window, visits all three screens, toggles dark mode, and closes without requiring manual interaction. It **needs a desktop display** (not a headless server).

## Screenshots

Add screenshots here after running the app locally:

- `screenshots/dashboard.png` — dashboard view
- `screenshots/transactions.png` — transactions view
- `screenshots/categories.png` — categories view

These are documentation placeholders, **not included files**.

## Project structure

```text
spendwise/
├── main.py
├── backend/
│   ├── __init__.py
│   ├── database.py
│   ├── expense_service.py
│   ├── category_service.py
│   └── settings_service.py
├── ui/
│   ├── __init__.py
│   ├── theme.py
│   ├── base_screen.py
│   ├── app_window.py
│   ├── dashboard_screen.py
│   ├── transactions_screen.py
│   ├── categories_screen.py
│   └── expense_form.py
├── tests/
│   ├── __init__.py
│   └── test_services.py
├── README.md
├── VIVA_NOTES.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Technology and why

| Technology | Role | Why it fits |
| --- | --- | --- |
| Python 3.10+ | Application language | Readable, easy to explain in a viva |
| tkinter / ttk | Desktop GUI | Shipped with standard Python on most systems |
| ttkbootstrap 1.10.1 | GUI theme layer | Uses tkinter's ttk widgets and built-in flatly/darkly themes |
| SQLite / sqlite3 | Persistent storage | No server or external account needed |
| Matplotlib 3.9.4 | One donut chart | Common plotting library embeddable in tkinter |
| unittest | Service tests | Included in Python standard library |
| csv | CSV export | Included in Python standard library |

**Design:** All database operations and business validation live in `backend/`. The user interface in `ui/` displays data and collects input. The app saves into `spendwise.db` beside `main.py` and creates it automatically. The file is ignored by Git. Dates use `YYYY-MM-DD`; filters, summaries, and exports query SQLite through parameterized statements.

**Sample data:** First initialization creates eight categories, forty realistic transactions over the current and previous two calendar months, and a monthly budget of ₹30,000. To restore the demo dataset, close the app and remove `spendwise.db` (this **permanently deletes your own saved entries**).

**Limits:** Intended for a single local user; no accounts, cloud sync, recurrence, or multi-currency support. Money is stored as SQLite `REAL` for simplicity; financial production apps typically use integer paise/decimal arithmetic instead.

## GitHub

Suggested repository description: **SpendWise — a modern Python tkinter expense tracker with SQLite, budgeting, filtering and a Matplotlib dashboard.**

Suggested topics: `python`, `tkinter`, `ttkbootstrap`, `sqlite`, `expense-tracker`, `matplotlib`, `desktop-app`, `university-project`

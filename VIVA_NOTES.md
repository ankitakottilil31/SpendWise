# SpendWise — Viva Notes

## 1. Architecture in plain English

SpendWise has three simple layers. `ui/` holds the tkinter screens and popup, which take input and show results without containing database SQL. `backend/` holds service classes that validate values, execute actions, and calculate summaries. `backend/database.py` creates and opens SQLite, which stores the three tables in a single local `spendwise.db` file. `main.py` starts the window and `ui/app_window.py` shares the service instances with the screens. This separation means I can test all the important spending rules without opening a window.

## 2. What happens when I press Add and save

1. I open **Transactions** in `ui/app_window.py` via `AppWindow.show_screen("Transactions")`.
2. The **Add** button triggers `TransactionsScreen.on_add_clicked()` in `ui/transactions_screen.py`.
3. That creates `ExpenseForm` from `ui/expense_form.py`, which shows amount, category, date picker, and note.
4. When I press Save, `ExpenseForm.save()` collects the values from the widgets.
5. It calls `ExpenseService.validate()` in `backend/expense_service.py`. The service checks positive, finite amount; real ISO date; and existing category ID.
6. If validation fails, the popup displays red messages under the relevant fields and keeps the form open.
7. If valid, `ExpenseForm.save()` calls `ExpenseService.save()`. It runs a parameterized `INSERT` or `UPDATE` query using the existing SQLite connection.
8. The service commits the transaction, the popup closes, and `TransactionsScreen.on_saved()` reloads the list and displays a ToastNotification.
9. The dashboard reloads its cards, budget Meter, donut, and recent entries when opened again.

## 3. Database schema and rationale

```sql
CREATE TABLE categories(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
CREATE TABLE expenses(
    id INTEGER PRIMARY KEY,
    amount REAL NOT NULL CHECK(amount > 0),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    date TEXT NOT NULL,
    note TEXT
);
CREATE TABLE settings(
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
PRAGMA foreign_keys = ON;
```

The foreign key `expenses.category_id` points to `categories.id`. With foreign keys enabled, SQLite does not allow an expense to refer to a nonexistent category, and will reject deleting categories still referenced by expenses. We also check that case first in `CategoryService.delete()` to show a friendly explanation. Dates are text in `YYYY-MM-DD` format so month filtering can use `substr(date,1,7)`. The settings row `monthly_budget` stores the budget number as text and `SettingsService` converts it to a float. SQLite is lightweight, bundled with Python, permanent, and needs no network or separate database server.

## 4. 25 likely viva questions and short answers

1. **What does SpendWise do?** Records expenses, filters them, displays trends and checks spending against a budget.
2. **Why tkinter?** It is a cross-platform GUI toolkit available with most Python installations.
3. **What is ttkbootstrap?** A theme layer on top of tkinter's `ttk`, providing modern built-in styles and widgets.
4. **Why not a website?** The task is a standalone local desktop program without hosting.
5. **What is SQLite?** A file-backed relational database accessed by Python's built-in `sqlite3` module.
6. **Why SQLite instead of MySQL?** It needs no external server, credentials, or installation for a small single-user project.
7. **What does OOP mean here?** Classes group related responsibilities: `ExpenseService` handles expense rules, and each screen class handles one view.
8. **What is inheritance?** Each screen inherits from `BaseScreen`, reusing the common header and notification method.
9. **What is a service layer?** Backend classes containing validation, SQL, and calculations, keeping UI code thin.
10. **How is an expense validated?** `ExpenseService.validate()` returns a dictionary of field-specific errors.
11. **Why reject zero and negative amounts?** A recorded expense must represent a positive spend.
12. **Why test for infinity and NaN?** Floating-point parsing accepts them, but they are not meaningful spending amounts.
13. **How are dates validated?** `date.fromisoformat()` verifies a real calendar date in the expected format.
14. **How do you avoid SQL injection?** Every user value is passed separately through parameterized `?` query placeholders.
15. **What does a foreign key do?** Ensures the category ID on an expense exists in the categories table.
16. **Why enable `PRAGMA foreign_keys = ON`?** SQLite requires foreign key enforcement to be enabled for each new connection.
17. **How do you search transactions?** A parameterized, case-insensitive `LIKE` query matches note text.
18. **How is the month filter implemented?** Compare the first seven date characters to `YYYY-MM`.
19. **How are dashboard totals calculated?** SQL `SUM(amount)` overall and for the current month.
20. **How is the top category found?** Group expense amounts per category and choose the largest total.
21. **How is the donut chart drawn?** Matplotlib `Figure` and `Axes.pie()` with a hole and a center total, embedded with `FigureCanvasTkAgg`.
22. **How does the budget Meter work?** Percentage is `this_month_spending / monthly_budget * 100`; green below 70%, yellow through 100%, and red above 100%.
23. **How does CSV export work?** Python's `csv.writer` writes the current filtered expenses with a header row.
24. **What are limitations?** It is offline and single-user; SQLite REAL amounts can have rounding errors, and there is no cloud syncing.
25. **How would you scale it?** Move to integer paise/decimal money values, add more tests, migrate to a client-server API/database, and add accounts only if required.

## 5. Two-minute demo script

**0:00–0:20 — Dashboard.** “This is SpendWise, my desktop expense tracker. The sidebar contains three screens. The dashboard immediately loads 40 seeded sample expenses and shows overall spending, this month's total, and the category with the highest spending.”

**0:20–0:40 — Meter and chart.** “The budget begins at ₹30,000. This Meter divides current-month expenses by the budget and changes color based on thresholds. The donut groups all spending by category, and the five newest entries appear below.” Click **Set budget**, enter a valid amount, and save.

**0:40–1:15 — Transactions.** “This table is a ttk Treeview. I can search by notes or filter by category and month.” Click **Add**, enter an amount, choose a category and date, write a note, then save. “The backend checks the values, writes to SQLite, and the table refreshes. Edit and delete are available, and deletion requires confirmation.” Show the search feature.

**1:15–1:35 — Categories and export.** “I can add categories. I cannot delete one already attached to expenses, because of the foreign-key relationship.” Open Transactions and point out **Export CSV**.

**1:35–1:50 — Themes.** Toggle dark mode. “The interface changes between ttkbootstrap's flatly and darkly themes, and the chart is recreated with matching background colors.”

**1:50–2:00 — Code.** “The UI is separate from the business services. Every SQL value is parameterized. I wrote in-memory unittest cases to check CRUD, filters, input validation, budgets and category safety.”

**Useful prep:** Run `python -m unittest discover tests` and `python main.py --check` before your demonstration.

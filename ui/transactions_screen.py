"""Searchable transactions table, CRUD actions and CSV export."""
import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ui.base_screen import BaseScreen
from ui.expense_form import ExpenseForm
from ui.theme import money, colors, BODY


class TransactionsScreen(BaseScreen):
    """Display filtered expense rows and command buttons."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Transactions", "Search, edit, and export every expense.")
        self.grid_rowconfigure(4, weight=1)
        self.build_toolbar()
        self.build_table()
        self.refresh()

    def build_toolbar(self):
        """Make search and filter controls above the transaction table."""
        filters = ttk.Frame(self)
        filters.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        filters.columnconfigure(0, weight=1)
        self.search = ttk.Entry(filters)
        self.search.insert(0, "")
        self.search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.search.bind("<KeyRelease>", lambda event: self.refresh_table())
        self.category = ttk.Combobox(filters, state="readonly", width=17)
        self.category.grid(row=0, column=1, padx=8)
        self.category.bind("<<ComboboxSelected>>", lambda event: self.refresh_table())
        self.month = ttk.Combobox(filters, state="readonly", width=13)
        self.month.grid(row=0, column=2, padx=(8, 0))
        self.month.bind("<<ComboboxSelected>>", lambda event: self.refresh_table())
        ttk.Label(filters, text="🔍 Search by note", bootstyle="secondary").grid(row=1, column=0, sticky="w")
        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, sticky="w", pady=(0, 16))
        for label, style, command in (
            ("+ Add", "success", self.on_add_clicked),
            ("Edit", "info-outline", self.on_edit_clicked),
            ("Delete", "danger-outline", self.on_delete_clicked),
            ("Export CSV", "secondary-outline", self.on_export_clicked),
        ):
            ttk.Button(buttons, text=label, bootstyle=style, command=command).pack(side="left", padx=(0, 8))

    def build_table(self):
        """Create the resizable Treeview and empty-state text."""
        area = ttk.Frame(self)
        area.grid(row=4, column=0, sticky="nsew")
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)
        columns = ("date", "category", "note", "amount")
        self.table = ttk.Treeview(area, columns=columns, show="headings", selectmode="browse")
        for name, width in (("date", 130), ("category", 170), ("note", 360), ("amount", 170)):
            self.table.heading(name, text=name.title())
            self.table.column(name, width=width, stretch=True, anchor="e" if name == "amount" else "w")
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(area, orient="vertical", command=self.table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scrollbar.set)
        self.empty = ttk.Label(self, text="No expenses found. Try different filters or add one.", bootstyle="secondary")
        self.empty.grid(row=5, column=0, sticky="w", pady=8)

    def refresh(self):
        """Reload category/month filter options without losing valid choices."""
        prior_category, prior_month = self.category.get(), self.month.get()
        self.category_names = {x["name"]: x["id"] for x in self.app.categories.list_all()}
        choices = ["All categories", *self.category_names]
        months = ["All months", *self.app.expenses.months()]
        self.category.configure(values=choices)
        self.month.configure(values=months)
        self.category.set(prior_category if prior_category in choices else choices[0])
        self.month.set(prior_month if prior_month in months else months[0])
        self.refresh_table()

    def refresh_table(self):
        """Render filtered transactions with alternating row colors."""
        category_id = self.category_names.get(self.category.get())
        month = self.month.get() if self.month.get() != "All months" else ""
        rows = self.app.expenses.list_all(self.search.get(), category_id, month)
        for item in self.table.get_children():
            self.table.delete(item)
        self.table.tag_configure("stripe", background=colors(self.app.dark)["stripe"])
        for index, row in enumerate(rows):
            self.table.insert("", "end", iid=str(row["id"]),
                              values=(row["date"], row["category"], row["note"], money(row["amount"])),
                              tags=("stripe",) if index % 2 else ())
        self.empty.configure(text="" if rows else "No expenses found. Try different filters or add one.")

    def selected_id(self):
        """Get the selected row identifier or show a subtle hint."""
        selected = self.table.selection()
        if not selected:
            self.app.set_status("Select a transaction first.")
            return None
        return int(selected[0])

    def on_saved(self, message):
        """Refresh related views after saving a transaction."""
        self.refresh()
        self.notify(message)

    def on_add_clicked(self):
        ExpenseForm(self.app, self.on_saved)

    def on_edit_clicked(self):
        key = self.selected_id()
        if key is not None:
            expense = self.app.expenses.get(key)
            if expense:
                ExpenseForm(self.app, self.on_saved, expense)

    def on_delete_clicked(self):
        key = self.selected_id()
        if key is None or not messagebox.askyesno("Delete expense", "Delete the selected expense?", parent=self):
            return
        try:
            self.app.expenses.delete(key)
        except ValueError as exc:
            self.app.set_status(str(exc))
            return
        self.refresh()
        self.notify("Expense deleted")

    def on_export_clicked(self):
        """Export the currently displayed filtered records to CSV."""
        path = filedialog.asksaveasfilename(parent=self, title="Export transactions",
                                            defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        category_id = self.category_names.get(self.category.get())
        month = self.month.get() if self.month.get() != "All months" else ""
        rows = self.app.expenses.list_all(self.search.get(), category_id, month)
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as output:
                writer = csv.writer(output)
                writer.writerow(["Date", "Category", "Note", "Amount (INR)"])
                writer.writerows((r["date"], r["category"], r["note"], f'{r["amount"]:.2f}') for r in rows)
        except OSError as exc:
            self.app.set_status(f"Export failed: {exc}")
            return
        self.notify(f"Exported {len(rows)} transactions")

"""Validated add/edit dialog using built-in ttkbootstrap inputs."""
from datetime import date
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from ui.theme import HEADING, BODY


class ExpenseForm(tk.Toplevel):
    """Collect fields and delegate every validation rule to ExpenseService."""

    def __init__(self, app, on_saved, expense=None):
        super().__init__(app)
        self.app, self.on_saved, self.expense = app, on_saved, expense
        self.title("Edit expense" if expense else "Add expense")
        self.geometry("440x550")
        self.resizable(False, False)
        self.transient(app)
        self.columnconfigure(0, weight=1)
        self.categories = app.categories.list_all()
        self.category_by_name = {x["name"]: x["id"] for x in self.categories}
        self.build_form()
        self.load_values()
        self.center()
        self.grab_set()

    def center(self):
        """Position dialog in the middle of the app window."""
        self.update_idletasks()
        x = self.app.winfo_rootx() + (self.app.winfo_width() - 440) // 2
        y = self.app.winfo_rooty() + (self.app.winfo_height() - 550) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def add_field(self, parent, name, title, widget):
        """Arrange label, input, and inline feedback consistently."""
        ttk.Label(parent, text=title, font=BODY).pack(anchor="w", pady=(12, 4))
        widget.pack(fill="x")
        error = ttk.Label(parent, text="", bootstyle="danger", font=("TkDefaultFont", 9))
        error.pack(anchor="w", pady=(2, 0))
        self.errors[name] = error

    def build_form(self):
        """Create the four expense inputs and action buttons."""
        body = ttk.Frame(self, padding=24)
        body.pack(fill="both", expand=True)
        self.errors = {}
        ttk.Label(body, text=self.title(), font=HEADING).pack(anchor="w")
        self.amount = ttk.Entry(body)
        self.add_field(body, "amount", "Amount (₹)", self.amount)
        self.category = ttk.Combobox(body, values=list(self.category_by_name), state="readonly")
        self.add_field(body, "category", "Category", self.category)
        self.date_picker = DateEntry(body, dateformat="%Y-%m-%d")
        self.add_field(body, "date", "Date", self.date_picker)
        self.note = ttk.Entry(body)
        ttk.Label(body, text="Note", font=BODY).pack(anchor="w", pady=(12, 4))
        self.note.pack(fill="x")
        buttons = ttk.Frame(body)
        buttons.pack(fill="x", pady=(24, 0))
        ttk.Button(buttons, text="Cancel", bootstyle="secondary-outline", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Save expense", bootstyle="success", command=self.save).pack(side="right", padx=8)

    def load_values(self):
        """Prepopulate edit mode, leaving add mode on today's date."""
        selected = self.expense
        if not selected:
            return
        self.amount.insert(0, str(selected["amount"]))
        name = next((x["name"] for x in self.categories if x["id"] == selected["category_id"]), "")
        self.category.set(name)
        self.date_picker.entry.delete(0, "end")
        self.date_picker.entry.insert(0, selected["date"])
        self.note.insert(0, selected["note"] or "")

    def save(self):
        """Show backend errors inline, or save and close the popup."""
        category_id = self.category_by_name.get(self.category.get())
        day = self.date_picker.entry.get().strip()
        amount = self.amount.get().strip()
        errors = self.app.expenses.validate(amount, category_id, day)
        for key, label in self.errors.items():
            label.configure(text=errors.get(key, ""))
        if errors:
            return
        try:
            expense_id = self.expense["id"] if self.expense else None
            self.app.expenses.save(amount, category_id, day, self.note.get(), expense_id)
        except (ValueError, Exception) as exc:
            self.errors["amount"].configure(text=f"Could not save: {exc}")
            return
        self.destroy()
        self.on_saved("Expense updated" if self.expense else "Expense added")

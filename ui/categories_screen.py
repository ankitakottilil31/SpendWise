"""Add and remove user-defined expense categories."""
from tkinter import messagebox
import ttkbootstrap as ttk
from ui.base_screen import BaseScreen
from ui.theme import HEADING, BODY


class CategoriesScreen(BaseScreen):
    """Manage category rows while protecting existing expense links."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Categories", "Organize your spending with simple labels.")
        self.grid_rowconfigure(2, weight=1)
        panel = ttk.Labelframe(self, text="Manage categories", padding=24)
        panel.grid(row=2, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        ttk.Label(panel, text="Category name", font=BODY).grid(row=0, column=0, sticky="w")
        self.entry = ttk.Entry(panel)
        self.entry.grid(row=1, column=0, sticky="ew", pady=8)
        ttk.Button(panel, text="Add category", bootstyle="success", command=self.on_add_clicked).grid(row=1, column=1, padx=8)
        self.feedback = ttk.Label(panel, text="", bootstyle="danger")
        self.feedback.grid(row=2, column=0, columnspan=2, sticky="w")
        self.table = ttk.Treeview(panel, columns=("name",), show="headings", height=10)
        self.table.heading("name", text="Category")
        self.table.column("name", anchor="w", stretch=True)
        self.table.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=16)
        panel.rowconfigure(3, weight=1)
        ttk.Button(panel, text="Delete selected", bootstyle="danger-outline", command=self.on_delete_clicked).grid(
            row=4, column=0, sticky="w"
        )
        self.refresh()

    def refresh(self):
        """Show the current category names."""
        for item in self.table.get_children():
            self.table.delete(item)
        for item in self.app.categories.list_all():
            self.table.insert("", "end", iid=str(item["id"]), values=(item["name"],))

    def on_add_clicked(self):
        """Validate through the service and show inline errors."""
        try:
            self.app.categories.add(self.entry.get())
        except ValueError as exc:
            self.feedback.configure(text=str(exc))
            return
        self.entry.delete(0, "end")
        self.feedback.configure(text="")
        self.refresh()
        self.notify("Category added")

    def on_delete_clicked(self):
        """Confirm deletion and display errors for linked expenses."""
        selected = self.table.selection()
        if not selected:
            self.feedback.configure(text="Select a category first.")
            return
        if not messagebox.askyesno("Delete category", "Delete this category?", parent=self):
            return
        try:
            self.app.categories.delete(int(selected[0]))
        except ValueError as exc:
            self.feedback.configure(text=str(exc))
            return
        self.feedback.configure(text="")
        self.refresh()
        self.notify("Category deleted")

"""Main application shell, navigation and theme switching."""
import tkinter as tk
import ttkbootstrap as ttk
from backend.database import connect, initialize
from backend.expense_service import ExpenseService
from backend.category_service import CategoryService
from backend.settings_service import SettingsService
from ui.dashboard_screen import DashboardScreen
from ui.transactions_screen import TransactionsScreen
from ui.categories_screen import CategoriesScreen
from ui.theme import BRAND, BODY, CAPTION, SIDEBAR_WIDTH, WINDOW_SIZE, MIN_SIZE


class AppWindow(ttk.Window):
    """Own the database, service instances, and active screen."""

    def __init__(self):
        super().__init__(themename="flatly")
        self.title("SpendWise • Expense Tracker")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.minsize(*MIN_SIZE)
        self.center_window()
        self.dark = False
        self.conn = connect()
        initialize(self.conn)
        self.expenses = ExpenseService(self.conn)
        self.categories = CategoryService(self.conn)
        self.settings = SettingsService(self.conn)
        self.buttons = {}
        self.screens = {}
        self.build_layout()
        self.show_screen("Dashboard")
        self.protocol("WM_DELETE_WINDOW", self.close)

    def center_window(self):
        """Center a resizable window on the current display."""
        width, height = WINDOW_SIZE
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def build_layout(self):
        """Create a fixed-width sidebar, flexible content and status bar."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        sidebar = ttk.Frame(self, padding=16, width=SIDEBAR_WIDTH)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(5, weight=1)
        ttk.Label(sidebar, text="💸 SpendWise", font=BRAND).grid(row=0, column=0, sticky="w", pady=(16, 32))
        for index, (name, label) in enumerate((
            ("Dashboard", "📊 Dashboard"), ("Transactions", "🧾 Transactions"), ("Categories", "🏷️ Categories")
        ), 1):
            button = ttk.Button(sidebar, text=label, bootstyle="primary-outline",
                                command=lambda target=name: self.show_screen(target))
            button.grid(row=index, column=0, sticky="ew", pady=8)
            self.buttons[name] = button
        self.toggle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(sidebar, text="Dark mode", variable=self.toggle_var,
                        bootstyle="round-toggle", command=self.toggle_theme).grid(row=6, column=0, sticky="w", pady=16)
        self.content = ttk.Frame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.status = ttk.Label(self, text="Ready • Sample expenses loaded", font=CAPTION,
                                padding=(16, 8), bootstyle="secondary")
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew")

    def show_screen(self, name):
        """Construct a screen on demand and refresh it on each visit."""
        types = {"Dashboard": DashboardScreen, "Transactions": TransactionsScreen,
                 "Categories": CategoriesScreen}
        if name not in self.screens:
            self.screens[name] = types[name](self.content, self)
            self.screens[name].grid(row=0, column=0, sticky="nsew")
        self.screens[name].tkraise()
        self.screens[name].refresh()
        for key, button in self.buttons.items():
            button.configure(bootstyle="primary" if key == name else "primary-outline")
        self.set_status(f"Viewing {name.lower()}")

    def toggle_theme(self):
        """Change builtin themes and refresh the theme-aware chart."""
        self.dark = self.toggle_var.get()
        self.style.theme_use("darkly" if self.dark else "flatly")
        for screen in self.screens.values():
            screen.refresh()
        self.set_status("Dark mode enabled" if self.dark else "Light mode enabled")

    def set_status(self, message):
        self.status.configure(text=message)

    def close(self):
        """Close SQLite gracefully before destroying the Tk window."""
        self.conn.close()
        self.destroy()

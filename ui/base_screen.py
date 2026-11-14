"""Shared header and notification helpers for app screens."""
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification
from ui.theme import TITLE, BODY, PAGE_PADDING


class BaseScreen(ttk.Frame):
    """Base container providing a consistent screen header."""

    def __init__(self, parent, app, title: str, subtitle: str):
        super().__init__(parent, padding=PAGE_PADDING)
        self.app = app
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text=title, font=TITLE).grid(row=0, column=0, sticky="w")
        ttk.Label(self, text=subtitle, font=BODY, bootstyle="secondary").grid(
            row=1, column=0, sticky="w", pady=(0, 24)
        )

    def notify(self, message: str) -> None:
        """Use nonblocking toast messages for successful actions."""
        self.app.set_status(message)
        ToastNotification(title="SpendWise", message=message, duration=2600, bootstyle="success").show_toast()

    def refresh(self) -> None:
        """Override in each child screen to load current data."""
        pass

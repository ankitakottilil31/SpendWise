"""Centralized visual tokens; no custom ttk styles or drawing."""
import sys

FONT = "Segoe UI" if sys.platform.startswith("win") else ("Helvetica Neue" if sys.platform == "darwin" else "DejaVu Sans")
TITLE = (FONT, 20, "bold")
NUMBER = (FONT, 24, "bold")
HEADING = (FONT, 13, "bold")
BODY = (FONT, 11)
CAPTION = (FONT, 9)
BRAND = (FONT, 17, "bold")
SPACING = 8
PAGE_PADDING = 24
SIDEBAR_WIDTH = 200
WINDOW_SIZE = (1100, 700)
MIN_SIZE = (900, 600)
PALETTE = ("#7C83FD", "#5CC8A1", "#F4B860", "#F07F8E", "#79B9F2", "#B297F6", "#6CCACC", "#C7A17A")
LIGHT = {"background": "#ffffff", "text": "#273449", "muted": "#718096", "stripe": "#F0F5FA"}
DARK = {"background": "#22262C", "text": "#F4F6FA", "muted": "#AFBAC9", "stripe": "#303840"}


def colors(dark: bool) -> dict[str, str]:
    """Return chart and list colors for the selected theme."""
    return DARK if dark else LIGHT


def money(value: float) -> str:
    """Format Indian-rupee amounts consistently."""
    return f"₹{value:,.2f}"

"""Dashboard with three cards, budget meter, donut and recent items."""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.widgets import Meter
from ui.base_screen import BaseScreen
from ui.theme import NUMBER, HEADING, BODY, CAPTION, PALETTE, money, colors


class DashboardScreen(BaseScreen):
    """Present calculated expenses and a monthly spending target."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Overview", "Your money, at a glance.")
        self.build_cards()
        self.build_sections()
        self.refresh()

    def build_cards(self):
        """Use only themed labels and frames for the three stats."""
        deck = ttk.Frame(self)
        deck.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        self.card_values = {}
        for index, (label, style) in enumerate((("Total Spent", "primary"), ("This Month", "success"), ("Top Category", "warning"))):
            deck.columnconfigure(index, weight=1, uniform="stats")
            panel = ttk.Labelframe(deck, text=label, padding=16, bootstyle=style)
            panel.grid(row=0, column=index, sticky="nsew", padx=(0, 8) if index < 2 else 0)
            ttk.Label(panel, text=label.upper(), font=CAPTION, bootstyle="secondary").pack(anchor="w")
            value = ttk.Label(panel, text="—", font=NUMBER)
            value.pack(anchor="w", pady=(8, 4))
            self.card_values[label] = value

    def build_sections(self):
        """Allocate flexible space to the chart and recent transaction list."""
        middle = ttk.Frame(self)
        middle.grid(row=3, column=0, sticky="nsew")
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=2)
        budget = ttk.Labelframe(middle, text="Monthly budget", padding=16)
        budget.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Button(budget, text="Set budget", bootstyle="primary-outline", command=self.on_budget_clicked).pack(anchor="e")
        self.meter_area = ttk.Frame(budget)
        self.meter_area.pack(expand=True, fill="both")
        chart = ttk.Labelframe(middle, text="Spending by category", padding=8)
        chart.grid(row=0, column=1, sticky="nsew")
        self.chart_area = ttk.Frame(chart)
        self.chart_area.pack(fill="both", expand=True)
        recent = ttk.Labelframe(self, text="Recent transactions", padding=16)
        recent.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        recent.columnconfigure(0, weight=1)
        self.recent_area = recent
        self.grid_rowconfigure(3, weight=1)

    def refresh(self):
        """Refresh all dashboard widgets after navigation or theme changes."""
        stats = self.app.expenses.summary()
        self.card_values["Total Spent"].configure(text=money(stats["total"]))
        self.card_values["This Month"].configure(text=money(stats["month"]))
        self.card_values["Top Category"].configure(text=stats["top_category"])
        self.draw_meter(stats["month"])
        self.draw_chart()
        self.draw_recent()

    def draw_meter(self, spent):
        """Select the built-in Meter color from budget thresholds."""
        for child in self.meter_area.winfo_children():
            child.destroy()
        budget = self.app.settings.get_budget()
        ratio = spent / budget * 100 if budget else 0
        style = "success" if ratio < 70 else ("warning" if ratio <= 100 else "danger")
        meter = Meter(self.meter_area, metersize=185, amounttotal=100,
                      amountused=min(100, round(ratio)), metertype="semi", bootstyle=style,
                      subtext="of monthly budget")
        meter.pack(pady=(8, 0))
        ttk.Label(self.meter_area, text=f"{ratio:.0f}% used", font=HEADING).pack()
        ttk.Label(self.meter_area, text=f"{money(spent)} / {money(budget)}", font=CAPTION,
                  bootstyle="secondary").pack(pady=8)

    def draw_chart(self):
        """Embed one Matplotlib donut, falling back to text if unavailable."""
        for child in self.chart_area.winfo_children():
            child.destroy()
        if hasattr(self, "figure"):
            try:
                from matplotlib import pyplot as plt
                plt.close(self.figure)
            except Exception:
                pass
        totals = self.app.expenses.category_totals()
        if not totals:
            ttk.Label(self.chart_area, text="No spending to chart yet.").pack(pady=32)
            return
        try:
            self.make_chart(totals)
        except Exception:
            for child in self.chart_area.winfo_children():
                child.destroy()
            for row in totals:
                ttk.Label(self.chart_area, text=f'{row["category"]}: {money(row["total"])}').pack(anchor="w", padx=16)

    def make_chart(self, totals):
        """Create a single donut with matching light/dark background."""
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        colorset = colors(self.app.dark)
        self.figure = Figure(figsize=(5, 2.8), dpi=100, facecolor=colorset["background"])
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(colorset["background"])
        wedges, _ = ax.pie([x["total"] for x in totals], colors=PALETTE[:len(totals)],
                           startangle=90, wedgeprops={"width": 0.32, "edgecolor": colorset["background"]})
        ax.text(0, 0, money(sum(x["total"] for x in totals)), ha="center", va="center",
                fontsize=11, weight="bold", color=colorset["text"])
        ax.legend(wedges, [x["category"] for x in totals], loc="center left",
                  bbox_to_anchor=(1, 0.5), frameon=False, fontsize=8, labelcolor=colorset["text"])
        self.figure.subplots_adjust(left=0.02, right=0.68, top=0.95, bottom=0.05)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=self.chart_area)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_recent(self):
        """Show the most recent five transactions in compact rows."""
        for child in self.recent_area.winfo_children():
            child.destroy()
        rows = self.app.expenses.list_all()[:5]
        if not rows:
            ttk.Label(self.recent_area, text="No transactions yet.").grid(row=0, column=0, sticky="w")
        for index, row in enumerate(rows):
            ttk.Label(self.recent_area, text=f'{row["date"]}   •   {row["category"]}   •   {row["note"] or "(No note)"}',
                      font=CAPTION).grid(row=index, column=0, sticky="w", pady=3)
            ttk.Label(self.recent_area, text=money(row["amount"]), font=CAPTION).grid(
                row=index, column=1, sticky="e", padx=16, pady=3)

    def on_budget_clicked(self):
        """Open a minimal popup with backend-validated budget input."""
        popup = tk.Toplevel(self.app)
        popup.title("Set monthly budget")
        popup.geometry("360x230")
        popup.transient(self.app)
        popup.resizable(False, False)
        body = ttk.Frame(popup, padding=24)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Monthly budget (₹)", font=HEADING).pack(anchor="w")
        entry = ttk.Entry(body)
        entry.insert(0, str(self.app.settings.get_budget()))
        entry.pack(fill="x", pady=12)
        feedback = ttk.Label(body, text="", bootstyle="danger")
        feedback.pack(anchor="w")
        def save_budget():
            try:
                self.app.settings.set_budget(entry.get())
            except ValueError as exc:
                feedback.configure(text=str(exc))
                return
            popup.destroy()
            self.refresh()
            self.notify("Monthly budget saved")
        ttk.Button(body, text="Save budget", bootstyle="success", command=save_budget).pack(anchor="e", pady=8)
        popup.grab_set()

"""SpendWise entry point; --check walks through screens without mainloop."""
import sys
from ui.app_window import AppWindow


def main() -> None:
    """Launch the app or run a short GUI smoke check."""
    app = AppWindow()
    if "--check" in sys.argv:
        try:
            for name in ("Dashboard", "Transactions", "Categories", "Dashboard"):
                app.show_screen(name)
                app.update_idletasks()
            app.toggle_var.set(True)
            app.toggle_theme()
            app.update_idletasks()
            print("GUI check passed: three screens and dark theme opened.")
        finally:
            app.close()
    else:
        app.mainloop()


if __name__ == "__main__":
    main()

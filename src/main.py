import tkinter as tk
from datetime import datetime
from tools.utils import Utils
from tools.theme_tools import ThemeManager
from forms.dashboard import ExpenseTrackerApp 


def main():
    root = tk.Tk()
    root.title(f"Expense Tracker ©{datetime.now().year}")
    Utils.set_app_icon(root, "assets/app_icon.png")
    app = ExpenseTrackerApp(root)
    ThemeManager(root).apply_theme() 
    root.mainloop()


if __name__ == "__main__":
    main()

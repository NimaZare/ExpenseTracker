import tkinter as tk
from datetime import datetime
from tools.utils import Utils
from database.migrations import migrate
from forms.dashboard import DashboardPage 


def main():
    migrate()

    root = tk.Tk()
    root.withdraw()

    root.title(f"Expense Tracker ©{datetime.now().year}")
    Utils.set_app_icon(root, "assets/app_icon.png")
    app = DashboardPage(root)

    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()

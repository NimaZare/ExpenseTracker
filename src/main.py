import tkinter as tk
from datetime import datetime
from tools.utils import Utils
from forms.dashboard import ExpenseTrackerApp 


def main():
    root = tk.Tk()
    root.withdraw()

    root.title(f"Expense Tracker ©{datetime.now().year}")
    Utils.set_app_icon(root, "assets/app_icon.png")
    app = ExpenseTrackerApp(root)

    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()

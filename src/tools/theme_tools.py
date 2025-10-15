import os
import sys
import json
import sv_ttk
import pywinstyles


class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.theme_file = "ExpenseTracker/src/tools/theme_preference.json"
        self.theme = self._load_theme_preference()

    def apply_theme(self):
        if self.theme == "dark":
            sv_ttk.set_theme("dark")
            pywinstyles.change_header_color(self.root, "#1c1c1c")
        else:
            sv_ttk.set_theme("light")
            pywinstyles.change_header_color(self.root, "#fafafa")

        version = sys.getwindowsversion()
        if version.major == 10 and version.build >= 22000:
            pywinstyles.change_header_color(self.root, "#1c1c1c" if self.theme == "dark" else "#fafafa")
        elif version.major == 10:
            pywinstyles.apply_style(self.root, "dark" if self.theme == "dark" else "normal")

        self.root.wm_attributes("-alpha", 0.99)
        self.root.wm_attributes("-alpha", 1)


    def save_theme_preference(self, theme):
        """Save the user's theme preference to a file."""
        with open(self.theme_file, "w") as file:
            json.dump({"theme": theme}, file)

        self.theme = theme


    def _load_theme_preference(self):
        """Load the user's theme preference from a file."""
        if os.path.exists(self.theme_file):
            with open(self.theme_file, "r") as file:
                data = json.load(file)
                return data.get("theme", "dark")
        return "dark"
    

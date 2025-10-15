import sys
import sv_ttk
import pywinstyles
from services.theme import ThemeService 


THEME_PREFERENCE_KEY = "app_theme"


class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.theme_service = ThemeService()
        self.theme = self._load_theme_preference() 

    def apply_theme(self):
        if self.theme == "dark":
            sv_ttk.set_theme("dark")
            header_color = "#1c1c1c"
        else:
            sv_ttk.set_theme("light")
            header_color = "#fafafa"

        if 'pywinstyles' in sys.modules:
            pywinstyles.change_header_color(self.root, header_color) 
            version = sys.getwindowsversion()
            if version.major == 10 and version.build >= 22000:
                pywinstyles.change_header_color(self.root, header_color) 
            elif version.major == 10:
                pywinstyles.apply_style(self.root, "dark" if self.theme == "dark" else "normal")


        self.root.wm_attributes("-alpha", 0.99)
        self.root.wm_attributes("-alpha", 1)


    def save_theme_preference(self, theme: str):
        """Save the user's theme preference to the database."""
        self.theme_service.update(THEME_PREFERENCE_KEY, theme) 
        self.theme = theme


    def _load_theme_preference(self) -> str:
        """Load the user's theme preference from the database."""
        preference = self.theme_service.get_by_item(THEME_PREFERENCE_KEY)
        
        if preference and preference.get('data'):
            return preference['data']
        
        return "dark"
    

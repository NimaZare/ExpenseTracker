import os
import sys
import tkinter as tk
from typing import List
from PIL import Image, ImageTk
from dotenv import load_dotenv


load_dotenv()


class Utils:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Get absolute path to resource, works for dev and for PyInstaller bundle.
        """
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        root_path = os.path.join(base_path, '..')
        return os.path.join(root_path, relative_path)
    

    @staticmethod
    def set_app_icon(root: tk.Tk, icon_relative_path: str):
        """
        Loads a PNG/ICO image using PIL and sets it as the window icon
        and taskbar icon using iconphoto.
        """
        icon_path = Utils.resource_path(icon_relative_path)

        try:
            if not os.path.exists(icon_path):
                print(f"Icon file not found at {icon_path}. Skipping icon load.")
                return
            
            pil_image = Image.open(icon_path)
            root._icon_photo = ImageTk.PhotoImage(pil_image)
            root.iconphoto(True, root._icon_photo)
        except ImportError:
            print("Error: Pillow library (PIL) not found. Cannot load PNG icon.")
        except Exception as e:
            print(f"Icon not loaded due to error: {e}")

    @staticmethod
    def get_default_categories() -> List[str]:
        """Fetches all default categories."""
        categories = os.getenv("DEFAULT_CATEGORIES", "").split(",")
        return [category.strip() for category in categories if category.strip()]

    @staticmethod
    def load_app_settings() -> dict:
        """Load application settings from a JSON file."""
        import json
        default_settings = {
            "currency": "$",
            "date_format": "YYYY-MM-DD",
            "theme": "Dark",
            "default_account": "Checking",
            "show_decimals": True,
            "auto_backup": False
        }

        settings_path = Utils.resource_path("data/app_settings.json")
        if not os.path.exists(settings_path):
            return default_settings
        
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            return settings
        except Exception as e:
            print(f"Error loading app settings: {e}")
            return default_settings

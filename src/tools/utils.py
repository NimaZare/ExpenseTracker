import os
import sys
import tkinter as tk
from PIL import Image, ImageTk


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

# pdfexpress.py

import platform

if platform.system() == "Windows":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(True)

import multiprocessing
import pathlib

from tkinterdnd2 import TkinterDnD


from config import PROJECT_NAME, PROJECT_VERSION
from toolkit.main_frame import MainFrame

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = TkinterDnD.Tk()
    root.title(f"{PROJECT_NAME} - Ver. {PROJECT_VERSION}")
    script_dir = pathlib.Path(__file__).parent
    icon_path = script_dir / "data" / "pdfexpress.ico"
    root.iconbitmap(icon_path)

    # Center the window
    window_width = 1280
    window_height = 768
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 4
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    app = MainFrame(root)
    root.mainloop()

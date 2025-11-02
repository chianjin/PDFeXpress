# src/pdfexpress.py
import platform

if platform.system() == "Windows":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(True)

import multiprocessing

from tkinterdnd2 import TkinterDnD

from toolkit.main_frame import MainFrame
from config import PROJECT_NAME, PROJECT_VERSION

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = TkinterDnD.Tk()
    root.title(f'{PROJECT_NAME} - Ver. {PROJECT_VERSION}')
    root.iconbitmap("data/pdfexpress.ico")
    root.geometry("1080x680")
    app = MainFrame(root)
    root.mainloop()

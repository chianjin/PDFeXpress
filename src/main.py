# src/main.py
import multiprocessing
import platform

from tkinterdnd2 import TkinterDnD  # 导入 TkinterDnD

from toolkit.app import MainFrame  # 导入 MainFrame
from toolkit.i18n import gettext_text as _

if __name__ == "__main__":
    if platform.system() == "Windows":
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(True)

    multiprocessing.freeze_support()
    root = TkinterDnD.Tk()
    root.title(_("Multifunctional PDF Toolkit"))
    root.geometry("1280x768")

    app = MainFrame(root)  # 实例化 MainFrame
    root.mainloop()

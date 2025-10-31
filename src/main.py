# src/main.py
import platform
import multiprocessing

from tkinterdnd2 import TkinterDnD  # 导入 TkinterDnD

from toolkit.app import MultiApp

if __name__ == "__main__":
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

    multiprocessing.freeze_support() 

    root= TkinterDnD.Tk()
    app= MultiApp(root)
    root.mainloop()
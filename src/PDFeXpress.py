import sys
import tkinter as tk

from app.FrameMenu import FrameMenu
from app.MainFrame import MainFrame
from constants import APP_ICON, APP_NAME, BASE_DIR
from utils import get_geometry


def run():
    if 'win' in sys.platform:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    root = tk.Tk()
    root.wm_geometry(get_geometry(root))
    root.title(APP_NAME)
    root.iconphoto(False, tk.PhotoImage(file=APP_ICON))
    menu = FrameMenu(root)
    root.configure(menu=menu)
    widget = MainFrame(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()


if __name__ == '__main__':
    run()

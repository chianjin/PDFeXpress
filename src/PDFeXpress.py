import ctypes
import sys
import tkinter as tk

from app.FrameMenu import FrameMenu
from app.MainFrame import MainFrame
from constants import APP_ICON, APP_NAME
from utils import get_geometry


def get_scale_factor():
    #  get ScaleFactor for windows, other platform always 100
    if sys.platform == 'win32':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        return ctypes.windll.shcore.GetScaleFactorForDevice(0)
    else:
        return 100


def run():
    scale_factor = get_scale_factor()
    root = tk.Tk()
    root.tk.call('tk', 'scaling', scale_factor / 75)
    root.wm_geometry(get_geometry(root))
    root.title(APP_NAME)
    root.iconbitmap(APP_ICON)
    menu = FrameMenu(root)
    root.configure(menu=menu)
    widget = MainFrame(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()


if __name__ == '__main__':
    run()

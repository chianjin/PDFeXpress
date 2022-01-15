import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

from app.FrameMenu import FrameMenu
from app.MainFrame import MainFrame
from constants import APP_ICON, APP_NAME
from utils import get_geometry


class PDFeXpress(tk.Tk):
    def __init__(self):
        super(PDFeXpress, self).__init__()

        if sys.platform not in ['win32', 'darwin']:
            ttk.Style(self).theme_use('clam')
            for font in tkfont.names(self):
                tkfont.nametofont(font).configure(size=9)

        self.wm_geometry(get_geometry(self))
        self.title(APP_NAME)
        self.iconphoto(False, tk.PhotoImage(file=APP_ICON))

        self.FrameMenu = FrameMenu(self)
        self.configure(menu=self.FrameMenu)

        self.MainFrame = MainFrame(self)
        self.MainFrame.pack(expand=True, fill='both')

    def run(self):
        self.mainloop()


if __name__ == '__main__':
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    PDFeXpress().run()

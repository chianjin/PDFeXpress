import sys
import tkinter as tk

from app.FrameMenu import FrameMenu
from app.MainFrame import MainFrame
from constants import APP_ICON, APP_NAME
from utils import get_geometry


class PDFeXpress(tk.Tk):
    def __init__(self):
        super(PDFeXpress, self).__init__()

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
    if 'win' in sys.platform:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    PDFeXpress().run()

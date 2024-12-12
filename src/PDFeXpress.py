import tkinter as tk

from app import Menubar
from constant import SYSTEM, BASE_FOLDER, APPLICATION_NAME
from main_frame import MainFrame
from utility import center_window


class PDFeXpress(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APPLICATION_NAME)
        self.iconbitmap(BASE_FOLDER / 'data/PDFeXpress.ico')
        self.geometry('1200x800')

        self.MainMenu = Menubar(self)
        self.configure(menu=self.MainMenu)
        self.MainFrame = MainFrame(self)
        self.MainFrame.pack(expand=True, fill='both', padx=4, pady=4)
        # self.state('zoomed')

        center_window(self, 128)

    def run(self):
        self.mainloop()


if __name__ == '__main__':
    if SYSTEM == 'Windows':
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(True)

    app = PDFeXpress()
    app.run()

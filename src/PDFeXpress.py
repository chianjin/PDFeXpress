import platform
import tkinter as tk
import tkinter.font as tkfont

from app.FrameMenu import FrameMenu
from app.MainFrame import MainFrame
from constants import APP_ICON, APP_NAME
from tkinterdnd2 import TkinterDnD


class PDFeXpress(TkinterDnD.Tk):
    def __init__(self):
        super(PDFeXpress, self).__init__()

        self._center()

        # for font in tkfont.names(self):
        #     tkfont.nametofont(font).configure(size=9)

        # FrameLabelFont: named font for frame label
        _frame_label_font = tkfont.Font(
                name='FrameLabelFont',
                family=tkfont.nametofont('TkDefaultFont').cget('family'),
                size=20,
                weight='bold'
                )

        self.FrameMenu = FrameMenu(self)
        self.configure(menu=self.FrameMenu)

        self.MainFrame = MainFrame(self)
        self.MainFrame.pack(expand=True, fill='both')

        self.title(APP_NAME)
        self.iconphoto(False, tk.PhotoImage(file=APP_ICON))

    def _center(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = screen_width * 2 // 3
        height = screen_height * 3 // 4
        screen_height = screen_height * 4 // 5
        left = (screen_width - width) // 2
        top = (screen_height - height) // 2
        self.wm_minsize(width, height)
        self.wm_resizable(True, True)
        self.wm_geometry(f'+{left}+{top}')

    def run(self):
        self.mainloop()


if __name__ == '__main__':
    if platform.system() == 'Windows' and int(platform.version().split('.')[0]) >= 10:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    PDFeXpress().run()

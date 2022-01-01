import pathlib
import tkinter as tk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiFrameMenu.ui"


class UiFrameMenu(tk.Menu):
    def __init__(self, master=None, **kw):
        super(UiFrameMenu, self).__init__(master, **kw)
        self.MenuFile = tk.Menu(self, tearoff='false')
        self.add(tk.CASCADE, menu=self.MenuFile, label='文件')
        self.mi_CommandQuit = 0
        self.MenuFile.add('command', label='退出')
        self.MenuFile.entryconfigure(self.mi_CommandQuit, command=self.quit)
        self.MenuHelp = tk.Menu(self, tearoff='false')
        self.add(tk.CASCADE, menu=self.MenuHelp, label='帮助')
        self.mi_CommandAbout = 0
        self.MenuHelp.add('command', label='关于')
        self.MenuHelp.entryconfigure(self.mi_CommandAbout, command=self.about)

    def quit(self):
        pass

    def about(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiFrameMenu(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()

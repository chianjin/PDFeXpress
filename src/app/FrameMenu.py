import tkinter as tk

from app.About import About
from constants import TRANSLATER as _


class FrameMenu(tk.Menu):
    def __init__(self, master=None, **kw):
        super(FrameMenu, self).__init__(master, **kw)
        self.MenuFile = tk.Menu(self, tearoff='false')
        self.add(tk.CASCADE, menu=self.MenuFile, label=_('File'))
        self.CommandQuit = 0
        self.MenuFile.add('command', label=_('Exit'))
        self.MenuFile.entryconfigure(self.CommandQuit, command=self.exit)
        self.MenuHelp = tk.Menu(self, tearoff='false')
        self.add(tk.CASCADE, menu=self.MenuHelp, label=_('Help'))
        self.CommandAbout = 0
        self.MenuHelp.add('command', label=_('About'))
        self.MenuHelp.entryconfigure(self.CommandAbout, command=self.about)

    def exit(self):
        self.master.quit()

    def about(self):
        about_frame = About(None)
        self.wait_window(about_frame)

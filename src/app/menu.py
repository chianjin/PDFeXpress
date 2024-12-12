import tkinter as tk
from tkinter import ttk

from app import About


class Menubar(tk.Menu):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self._style = ttk.Style(self.master)
        self.theme = tk.StringVar(value=self._style.theme_use())

        self.MenuFile = tk.Menu(self, tearoff=False)
        self.MenuFile.add_command(label=_('Exit'), command=self.exit)
        self.add_cascade(label=_('File'), menu=self.MenuFile)

        self.MenuTheme = tk.Menu(self, tearoff=False)
        for theme in self._style.theme_names():
            self.MenuTheme.add_radiobutton(label=theme, command=self.set_theme, value=theme, variable=self.theme)
        self.add_cascade(label=_('Theme'), menu=self.MenuTheme)

        self.MenuHelp = tk.Menu(self, tearoff=False)
        self.MenuHelp.add_command(label=_('About'), command=self.about)
        self.add_cascade(label=_('Help'), menu=self.MenuHelp)

        self.configure(tearoff=False)

    def exit(self):
        self.master.destroy()

    def set_theme(self):
        self._style.theme_use(self.theme.get())

    def about(self):
        self.wait_window(About(None))

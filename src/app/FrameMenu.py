import tkinter as tk

from app.About import About


class FrameMenu(tk.Menu):
    def __init__(self, master=None, **kw):
        super(FrameMenu, self).__init__(master, **kw)

        self.MenuFile = tk.Menu(self, tearoff=False)
        self.MenuFile.add_command(label=_('Exit'), command=self.exit)
        self.add_cascade(label=_('File'), menu=self.MenuFile)

        self.MenuHelp = tk.Menu(self, tearoff=False)
        self.MenuHelp.add_command(label=_('About'), command=self.about)
        self.add_cascade(label=_('Help'), menu=self.MenuHelp)

    def exit(self):
        self.master.quit()

    def about(self):
        about_frame = About(None)
        self.wait_window(about_frame)

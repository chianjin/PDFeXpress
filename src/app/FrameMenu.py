from app.About import About
from ui.UiFrameMenu import UiFrameMenu


class FrameMenu(UiFrameMenu):
    def __init__(self, master=None, **kw):
        super(FrameMenu, self).__init__(master=master, **kw)

    def quit(self):
        self.master.quit()

    def about(self):
        About(None)

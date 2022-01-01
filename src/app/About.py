import webbrowser

from constants import APP_NAME, APP_URL, APP_VERSION
from ui.UiAbout import UiAbout
from utils import get_geometry


class About(UiAbout):
    def __init__(self, master=None, **kw):
        super(About, self).__init__(master, **kw)
        self.geometry(get_geometry(self, None))

        self.app_name.set(APP_NAME)
        self.app_version.set(APP_VERSION)
        self.app_url.set(APP_URL)

        self.grab_set()

    def open_url(self, event=None):
        webbrowser.open_new_tab(APP_URL)

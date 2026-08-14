from tkinter import ttk

from util.helpers import get_title_font
from util.i18n import gettext_text as _


class NotImplementedFrame(ttk.Frame):
    def __init__(self, master, text='', **kwargs):
        super().__init__(master, **kwargs)

        if text:
            text = f'{text} {_("Not implemented")}'
        else:
            text = _('Not implemented')

        font = get_title_font()
        ttk.Label(self, text=text, font=font).pack(padx=20, pady=50)

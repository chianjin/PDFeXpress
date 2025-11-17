from tkinter import font as tkfont
from tkinter import ttk

from toolkit.i18n import gettext_text as _


class TitleFrame(ttk.Frame):
    """Display the title of app"""

    def __init__(self, parent, text=_('Title'), **kwargs):
        super().__init__(parent, **kwargs)
        default_font = tkfont.nametofont('TkDefaultFont')
        font = tkfont.Font(family=default_font['family'], size=18, weight='bold')
        self.LabelTitle = ttk.Label(self, text=text, font=font)
        self.LabelTitle.grid(row=0, column=0, sticky='w', padx=(20, 5), pady=5)


class OptionFrame(ttk.Labelframe):
    def __init__(self, parent, text=_('Options'), **kwargs):
        super().__init__(parent, text=text, **kwargs)


if __name__ == '__main__':
    import tkinter as tk

    root = tk.Tk()
    title = TitleFrame(root)
    title.pack(fill='x', padx=10, pady=10)
    option = OptionFrame(root)
    label = ttk.Label(option, text='Options')
    label.pack()
    option.pack(fill='x', padx=10, pady=10)
    root.mainloop()

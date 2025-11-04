# toolkit/ui/widget/url.py

import tkinter as tk
import webbrowser
from tkinter import font as tkfont


class URLLabel(tk.Label):
    def __init__(self, parent, url, text=None, **kwargs):
        super().__init__(parent, **kwargs)

        normal_color = "blue"
        hold_color = "darkblue"

        font = tkfont.nametofont("TkDefaultFont").actual()
        size = font["size"]
        font = tkfont.Font(size=size, underline=True)

        if not text:
            text = url

        self.configure(text=text, font=font, fg=normal_color, cursor="hand2")
        self.bind("<Button-1>", lambda e: webbrowser.open(url))
        self.bind("<Enter>", lambda e: self.config(fg=hold_color))
        self.bind("<Leave>", lambda e: self.config(fg=normal_color))

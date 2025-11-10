import tkinter as tk
from tkinter import ttk

class HelpWindow(tk.Toplevel):
    def __init__(self, parent, title, help_text, on_close=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_close = on_close
        self.title(title)
        # self.transient(parent)

        label = ttk.Label(
            self, text=help_text, wraplength=500, justify="left", relief='groove',
            padding = 20, background="white"
        )
        label.pack(padx=20, pady=20)
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=(0, 30))

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def destroy(self):
        if self.on_close:
            self.on_close()
        super().destroy()

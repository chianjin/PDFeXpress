# toolkit/ui/framework/progress_dialog.py

import tkinter as tk
from tkinter import ttk

from toolkit.i18n import gettext_text as _


class ProgressDialog(tk.Toplevel):
    """Modal progress bar dialog."""

    def __init__(self, master, title, label_text, cancel_command):
        super().__init__(master)
        self.title(title)
        self.transient(master)
        self.grab_set()  # set to modal, intercept master input
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(padx=20, pady=10)

        self.progressbar = ttk.Progressbar(
            self, orient="horizontal", length=300, mode="indeterminate"
        )
        self.progressbar.pack(padx=20, pady=5)
        self.progressbar.start(10)  # start with indeterminate mode

        self.cancel_button = ttk.Button(self, text=_("Cancel"), command=cancel_command)
        self.cancel_button.pack(pady=10)

        self.update_idletasks()
        master_x = master.winfo_x()
        master_y = master.winfo_y()
        master_width = master.winfo_width()
        master_height = master.winfo_height()

        self_width = self.winfo_width()
        self_height = self.winfo_height()

        x = master_x + (master_width - self_width) // 2
        y = master_y + (master_height - self_height) // 4
        self.geometry(f"+{x}+{y}")

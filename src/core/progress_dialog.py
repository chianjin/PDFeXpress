import tkinter as tk
from tkinter import ttk

from util.i18n import gettext_text as _


class ProgressDialog(tk.Toplevel):
    """Modal progress bar dialog.

    mode='indeterminate' (default) keeps the original busy-bar behaviour.
    mode='determinate' shows a real percentage that is updated via
    set_progress().
    """

    def __init__(self, master, title, label_text, cancel_command, mode='indeterminate'):
        super().__init__(master)

        self.withdraw()
        self.title(title)
        self.grab_set()

        self._mode = mode

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(padx=20, pady=10)

        self.progressbar = ttk.Progressbar(
            self, orient='horizontal', length=300, mode=mode
        )
        self.progressbar.pack(padx=20, pady=5)
        if mode == 'indeterminate':
            self.progressbar.start(10)
        else:
            self.progressbar['maximum'] = 100
            self.progressbar['value'] = 0

        self.cancel_button = ttk.Button(self, text=_('Cancel'), command=cancel_command)
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
        self.geometry(f'+{x}+{y}')
        self.deiconify()

    def set_progress(self, fraction, label_text=None):
        """Update progress.

        fraction: 0..1 (ignored in indeterminate mode)
        label_text: optional new status text
        """
        if self._mode == 'determinate':
            value = max(0, min(100, int(round(fraction * 100))))
            self.progressbar['value'] = value
        if label_text is not None:
            self.label.config(text=label_text)
        self.update_idletasks()

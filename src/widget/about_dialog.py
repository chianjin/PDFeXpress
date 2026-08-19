import tkinter as tk
import webbrowser
from tkinter import ttk

from config import PROJECT_AUTHOR, PROJECT_NAME, PROJECT_URL, PROJECT_VERSION
from util.helpers import get_title_font
from util.i18n import gettext_text as _


class AboutDialog(tk.Toplevel):
    # DIALOG_WIDTH = 600

    def __init__(self, master=None):
        super().__init__(master)
        self.title(f'{PROJECT_NAME} - Ver. {PROJECT_VERSION}')
        self.resizable(False, False)
        self.transient(master)

        self._setup_ui()

        self.update_idletasks()

        self._center_on_master()
        self.grab_set()
        self.wait_window(self)

    def _setup_ui(self):
        container = ttk.Frame(self, padding=(50, 25))
        container.pack(fill=tk.BOTH, expand=True)

        title_font = get_title_font()
        version_font = (title_font[0], 12, 'bold')

        ttk.Label(
            container,
            text=PROJECT_NAME,
            font=title_font,
            anchor='center',
        ).pack(fill=tk.X, pady=(0, 8))

        ttk.Label(
            container,
            text=_('Version {}').format(PROJECT_VERSION),
            font=version_font,
            anchor='center',
        ).pack(fill=tk.X)

        url_label = tk.Label(
            container,
            text=PROJECT_URL,
            fg='blue',
            cursor='hand2',
            font=(title_font[0], 9, 'underline'),
        )
        url_label.pack(fill=tk.X, pady=(8, 12))
        url_label.bind('<Button-1>', lambda _event: webbrowser.open(PROJECT_URL, new=2))

        ttk.Label(
            container,
            text=_('Copyright © {}-{} {}, all rights reserved.').format('2022', '2026', PROJECT_AUTHOR),
            anchor='center',
        ).pack(fill=tk.X, pady=(0, 18))

        ttk.Label(
            container,
            text=_('------ Third-party software or packages ------'),
            anchor='center',
        ).pack(fill=tk.X, pady=(0, 12))

        third_party_frame = ttk.Frame(container)
        third_party_frame.pack(fill=tk.X, pady=(0, 18))
        # third_party_frame.columnconfigure(0, weight=1, uniform="col")
        third_party_frame.columnconfigure(1, weight=1, uniform='col')

        libraries = [
            (
                'Python',
                'Python Software Foundation License v2',
                'https://www.python.org/',
            ),
            (
                'PyMuPDF',
                'GNU AFFERO GPL 3.0 or Artifex Commercial License',
                'https://github.com/pymupdf/PyMuPDF',
            ),
            ('Pillow', 'MIT-CMU', 'https://python-pillow.org/'),
            ('tkinterdnd2', 'MIT License', 'https://github.com/Eliav2/tkinterdnd2'),
        ]

        for row, (name, license_text, url) in enumerate(libraries):
            name_label = tk.Label(
                third_party_frame,
                text=name,
                fg='blue',
                cursor='hand2',
                font=(title_font[0], 9, 'underline'),
            )
            name_label.grid(row=row, column=0, sticky='e', padx=(0, 15), pady=3)
            name_label.bind('<Button-1>', lambda _event, u=url: webbrowser.open(u, new=2))
            ttk.Label(
                third_party_frame,
                text=license_text,
                anchor='w',
            ).grid(row=row, column=1, sticky='w', pady=3)

        ttk.Button(
            container,
            text=_('OK'),
            command=self.destroy,
        ).pack(pady=(5, 0))

    def _center_on_master(self):
        self.update_idletasks()
        master = self.master
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f'+{x}+{y}')

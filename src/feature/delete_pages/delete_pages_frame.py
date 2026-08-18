import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import showerror

import pymupdf

from config import EXECUTABLE_PATH
from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.helpers import enable_pdf_drop
from util.i18n import gettext_text as _
from util.page_range_parser import parse_page_ranges
from widget import HelpWindow


class DeletePagesFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='delete_pages', **kw)
        self._delete_groups: list[list[int]] = []
        self._delete_raw: list[str] = []
        self._total_pages = 0

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))
        self.input_path = tk.StringVar()

        row = ttk.Frame(self.input_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self.input_path, state='readonly').pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(row, text=_('Browser'), command=self._set_input_path).pack(
            side='left', padx=(5, 0)
        )

        # Fixed single-input: collapse to natural height (same reasoning as
        # interleave_merge / split_pdf - no list to stretch, avoid a large void).
        self.input_frame.pack_configure(expand=False, fill='x')
        enable_pdf_drop(self.input_frame, self.input_path)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output Folder'))
        self.output_path = tk.StringVar()
        ttk.Entry(
            self.output_frame, textvariable=self.output_path, state='readonly'
        ).pack(side='left', fill='x', expand=True)
        ttk.Button(
            self.output_frame, text=_('Browser'), command=self._set_output_folder
        ).pack(side='left', padx=(5, 0))

    def _setup_options_frame(self):
        ttk.Label(self.options_frame, text=_('Pages to delete')).pack(side='left')
        self.range_expr = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self.range_expr, width=40).pack(
            side='left', fill='x', padx=(5, 0)
        )
        self.help_icon = tk.PhotoImage(file=EXECUTABLE_PATH / 'asset/icon/help.png')
        ttk.Button(
            self.options_frame,
            text=_('Help'),
            image=self.help_icon,
            style='Toolbutton',
            command=self._open_help,
        ).pack(side='left', padx=(5, 0))
        ttk.Label(
            self.options_frame,
            text=_('Example: "3,7-9,12;:2". Click Help for details.'),
        ).pack(side='left', padx=(5, 0))

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _set_input_path(self):
        path = askopenfilename(filetypes=FILE_TYPES['PDF'])
        if path:
            self.input_path.set(Path(path))

    def _open_help(self):
        posix_lang = os.environ.get('LANG', 'en_US.UTF-8')
        language = posix_lang.split('.')[0]
        guide_path = (
                EXECUTABLE_PATH / f'asset/guide/page_range_syntax_guide-{language}.txt'
        )
        if not guide_path.exists():
            guide_path = (
                    EXECUTABLE_PATH / 'asset/guide/page_range_syntax_guide-en_US.txt'
            )
        with open(guide_path, encoding='UTF-8') as f:
            help_content = f.readlines()
        title = help_content[0].strip()
        content = ''.join(help_content)
        HelpWindow(self, title=title, content=content).focus()

    def _set_output_folder(self):
        folder = askdirectory(mustexist=True)
        if folder:
            self.output_path.set(Path(folder))

    def get_input_paths(self):
        return [Path(self.input_path.get())] if self.input_path.get() else []

    def get_output_path(self):
        output_path = self.output_path.get()
        if output_path:
            return Path(self.output_path.get())
        return None

    def get_options(self) -> dict:
        return {
            'groups': self._delete_groups,
            'raw_groups': self._delete_raw,
            'total_pages': self._total_pages,
        }

    def _execute_handler(self):
        if not self._validate_execute_params():
            return
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        from feature.delete_pages.delete_pages_worker import (
            run_delete_pages_with_progress,
        )

        run_delete_pages_with_progress(self.winfo_toplevel(), params)

    def _validate_execute_params(self):
        src = self.input_path.get()
        if not src:
            showerror(title=_('Error'), message=_('Input PDF must be set.'))
            return False
        if not Path(src).is_file():
            showerror(title=_('Error'), message=_('Input PDF does not exist.'))
            return False
        if not self.output_path.get():
            showerror(title=_('Error'), message=_('Output folder must be set.'))
            return False
        expr = self.range_expr.get().strip()
        if not expr:
            showerror(title=_('Error'), message=_('Pages to delete must be set.'))
            return False
        if expr.startswith('+'):
            showerror(
                title=_('Error'), message=_('Enhanced mode (+) is not supported.')
            )
            return False
        try:
            with pymupdf.open(Path(self.input_path.get())) as doc:
                total = doc.page_count
            groups = parse_page_ranges(expr, total)
            if not groups:
                raise ValueError(_('Range expression produced no pages.'))
            raw_groups = [g.strip() for g in expr.split(';') if g.strip()]
            if len(groups) != len(raw_groups):
                raw_groups = raw_groups[: len(groups)]
            self._delete_groups = groups
            self._delete_raw = raw_groups
            self._total_pages = total
        except Exception as exc:
            showerror(title=_('Error'), message=f'{type(exc).__name__}: {exc}')
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    DeletePagesFrame(root).pack(fill='both', expand=True)
    root.mainloop()

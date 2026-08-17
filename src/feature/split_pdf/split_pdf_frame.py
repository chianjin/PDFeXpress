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


class SplitPdfFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='split_pdf', **kw)
        self._total_pages = 0
        self._split_groups: list[list[int]] = []
        self._split_group_exprs: list[str] = []

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
        # interleave_merge - no list to stretch, avoid a large void).
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
        radio_frame = ttk.Frame(self.options_frame)

        self._mode = tk.StringVar(value='single')
        ttk.Radiobutton(
            radio_frame,
            text=_('Single Page'),
            variable=self._mode,
            value='single',
            command=self._on_mode_change,
        ).pack(side='left')
        ttk.Radiobutton(
            radio_frame,
            text=_('By Page Count'),
            variable=self._mode,
            value='by_pages',
            command=self._on_mode_change,
        ).pack(side='left', padx=(5, 0))
        ttk.Radiobutton(
            radio_frame,
            text=_('By Parts'),
            variable=self._mode,
            value='by_parts',
            command=self._on_mode_change,
        ).pack(side='left', padx=(5, 0))
        ttk.Radiobutton(
            radio_frame,
            text=_('Custom Range'),
            variable=self._mode,
            value='custom',
            command=self._on_mode_change,
        ).pack(side='left', padx=(5, 5))
        self._param_label = ttk.Label(radio_frame, text=_('Pages per chunk'))
        self._param_label.pack(side='left', padx=(5, 0))
        self._help_icon = tk.PhotoImage(file=EXECUTABLE_PATH / 'asset/icon/help.png')
        ttk.Button(
            radio_frame,
            image=self._help_icon,
            style='Toolbutton',
            command=self._open_help,
        ).pack(side='left')
        self._param_entry = tk.StringVar()
        self._param_entry_widget = ttk.Entry(
            radio_frame, textvariable=self._param_entry, width=30
        )
        self._param_entry_widget.pack(side='left', padx=(0, 5))
        radio_frame.pack(fill='x')

        # Single parameter Entry whose meaning depends on the selected mode:
        #   by_pages -> pages per chunk (integer)
        #   by_parts -> number of parts (integer)
        #   custom   -> range expression (string)
        #   single   -> unused, disabled
        help_text = _(
            'By Page Count/By Parts: Int, for example: 5. Custom Range: "1-5;7-:2". Click Help for details.'
        )
        ttk.Label(self.options_frame, text=help_text).pack(side='left')
        self._on_mode_change()

    def _on_mode_change(self):
        mode = self._mode.get()
        if mode == 'single':
            self._param_label.configure(text=_('No parameter'))
            self._param_entry.set('')
            self._param_entry_widget.configure(state='disabled')
        else:
            self._param_entry_widget.configure(state='normal')
            if mode == 'by_pages':
                self._param_label.configure(text=_('Pages per chunk'))
            elif mode == 'by_parts':
                self._param_label.configure(text=_('Number of parts'))
            elif mode == 'custom':
                self._param_label.configure(text=_('Range expression'))

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
            self.output_path.set(Path(path).parent)

    def _set_output_folder(self):
        folder = askdirectory(mustexist=True)
        if folder:
            self.output_path.set(Path(folder))

    def get_input_paths(self):
        return [Path(self.input_path.get())]

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        entry = self._param_entry.get().strip()
        mode = self._mode.get()
        opts = {'mode': mode, 'total_pages': self._total_pages}
        if mode == 'by_pages':
            opts['pages_per_chunk'] = int(entry) if entry else 1
        elif mode == 'by_parts':
            opts['parts'] = int(entry) if entry else 2
        elif mode == 'custom':
            opts['groups'] = self._split_groups
            opts['group_exprs'] = self._split_group_exprs
        return opts

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_execute_params():
            from feature.split_pdf.split_pdf_worker import run_split_with_progress

            run_split_with_progress(self.winfo_toplevel(), params)

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
        mode = self._mode.get()
        entry = self._param_entry.get().strip()
        if mode == 'by_pages':
            if not entry:
                showerror(title=_('Error'), message=_('Pages per chunk must be set.'))
                return False
            try:
                n = int(entry)
            except ValueError:
                showerror(
                    title=_('Error'), message=_('Pages per chunk must be an integer.')
                )
                return False
            if n < 1:
                showerror(
                    title=_('Error'), message=_('Pages per chunk must be at least 1.')
                )
                return False
        elif mode == 'by_parts':
            if not entry:
                showerror(title=_('Error'), message=_('Number of parts must be set.'))
                return False
            try:
                n = int(entry)
            except ValueError:
                showerror(
                    title=_('Error'), message=_('Number of parts must be an integer.')
                )
                return False
            if n < 1:
                showerror(
                    title=_('Error'), message=_('Number of parts must be at least 1.')
                )
                return False
        elif mode == 'custom':
            if not entry:
                showerror(title=_('Error'), message=_('Range expression must be set.'))
                return False
        try:
            with pymupdf.open(Path(self.input_path.get())) as doc:
                total = doc.page_count
            self._total_pages = total
            if mode == 'custom':
                groups = parse_page_ranges(entry, total)
                if not groups:
                    raise ValueError(_('Range expression produced no pages.'))
                group_exprs = [g.strip() for g in entry.split(';') if g.strip()]
                if len(groups) != len(group_exprs):
                    group_exprs = group_exprs[: len(groups)]
                self._split_groups = groups
                self._split_group_exprs = group_exprs
        except Exception as exc:
            showerror(title=_('Error'), message=f'{type(exc).__name__}: {exc}')
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    SplitPdfFrame(root).pack(fill='both', expand=True)
    root.mainloop()

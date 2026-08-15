import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import showerror

from config import EXECUTIVE_PATH
from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.i18n import gettext_text as _


class SplitPdfFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='split_pdf', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))
        self.input_path = tk.StringVar()

        row = ttk.Frame(self.input_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self.input_path).pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(row, text=_('Browser'), command=self._browse_input).pack(
            side='left', padx=(5, 0)
        )

        # Fixed single-input: collapse to natural height (same reasoning as
        # interleave_merge - no list to stretch, avoid a large void).
        self.input_frame.pack_configure(expand=False, fill='x')

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output Folder'))
        self.output_path = tk.StringVar()
        ttk.Entry(self.output_frame, textvariable=self.output_path).pack(
            side='left', fill='x', expand=True
        )
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
        self._help_icon = tk.PhotoImage(file=EXECUTIVE_PATH / 'asset/icon/help.png')
        ttk.Button(radio_frame, image=self._help_icon, style='Toolbutton').pack(
            side='left'
        )
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
            'By Page Count/By Parts: Int, for example: 5. Custom Range: "1-5;7-:2". Click Help for detail.'
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

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _browse_input(self):
        init = self._initial_dir(self.input_path.get())
        path = askopenfilename(filetypes=FILE_TYPES['PDF'], initialdir=init)
        if path:
            self.input_path.set(Path(path))

    @staticmethod
    def _initial_dir(current: str) -> Path | str:
        if current:
            return Path(current).parent
        return ''

    def _set_output_folder(self):
        init_dir = ''
        current = self.output_path.get()
        if current:
            init_dir = Path(current)
        elif self.input_path.get():
            init_dir = Path(self.input_path.get()).parent
        folder = askdirectory(initialdir=init_dir)
        if folder:
            self.output_path.set(Path(folder))

    def get_input_paths(self):
        return [Path(self.input_path.get())]

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        entry = self._param_entry.get().strip()
        mode = self._mode.get()
        opts = {'mode': mode}
        if mode == 'by_pages':
            opts['pages_per_chunk'] = int(entry) if entry else 1
        elif mode == 'by_parts':
            opts['parts'] = int(entry) if entry else 2
        elif mode == 'custom':
            opts['range_expr'] = entry
        return opts

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.split_pdf.split_pdf_worker import run_split_with_progress

            run_split_with_progress(self.winfo_toplevel(), params)

    def _validate_input_files(self):
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
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    SplitPdfFrame(root).pack(fill='both', expand=True)
    root.mainloop()

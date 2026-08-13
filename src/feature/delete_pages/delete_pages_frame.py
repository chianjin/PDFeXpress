import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showerror
from pathlib import Path

from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _
from util.file_types import FILE_TYPES


class DeletePagesFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='delete_pages', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))
        self.input_path = tk.StringVar()

        row = ttk.Frame(self.input_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Label(row, text=_('PDF')).pack(side='left', padx=(0, 5))
        ttk.Entry(row, textvariable=self.input_path).pack(side='left', expand=True, fill='x')
        ttk.Button(row, text=_('Browser'), command=self._browse_input).pack(side='left', padx=(5, 0))

        # Fixed single-input: collapse to natural height (same reasoning as
        # interleave_merge / split_pdf - no list to stretch, avoid a large void).
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
        ttk.Label(self.options_frame, text=_('Pages to delete')).pack(
            side=tk.TOP, anchor='w', pady=(2, 4)
        )
        self.range_expr = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self.range_expr, width=40).pack(
            side=tk.TOP, fill='x', pady=(0, 4)
        )

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame, text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _browse_input(self):
        init = self._initial_dir(self.input_path.get())
        path = askopenfilename(filetypes=FILE_TYPES['PDF'], initialdir=init)
        if path:
            self.input_path.set(str(Path(path)))

    @staticmethod
    def _initial_dir(current: str) -> str:
        if current:
            return str(Path(current).parent)
        return ''

    def _set_output_folder(self):
        init_dir = ''
        current = self.output_path.get()
        if current:
            init_dir = str(Path(current))
        elif self.input_path.get():
            init_dir = str(Path(self.input_path.get()).parent)
        folder = askdirectory(initialdir=init_dir)
        if folder:
            self.output_path.set(str(Path(folder)))

    def get_input_pathes(self):
        return [Path(self.input_path.get())]

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {
            'range_expr': self.range_expr.get().strip(),
        }

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_pathes(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.delete_pages.delete_pages_worker import run_delete_with_progress
            run_delete_with_progress(self.winfo_toplevel(), params)

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
        expr = self.range_expr.get().strip()
        if not expr:
            showerror(title=_('Error'), message=_('Pages to delete must be set.'))
            return False
        if expr.startswith('+'):
            showerror(title=_('Error'), message=_('Enhanced mode (+) is not supported.'))
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    DeletePagesFrame(root).pack(fill='both', expand=True)
    root.mainloop()

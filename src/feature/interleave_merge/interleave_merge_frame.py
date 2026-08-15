import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror

from tkinterdnd2 import TkinterDnD

from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.i18n import gettext_text as _


class InterleaveMergeFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='interleave_merge', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))

        self.pdf_a = tk.StringVar()
        self.pdf_b = tk.StringVar()

        row_a = ttk.Frame(self.input_frame)
        row_a.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Label(row_a, text='PDF A').pack(side='left', padx=(0, 5))
        ttk.Entry(row_a, textvariable=self.pdf_a).pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(row_a, text=_('Browser'), command=self._browse_a).pack(
            side='left', padx=(5, 0)
        )

        row_b = ttk.Frame(self.input_frame)
        row_b.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Label(row_b, text='PDF B').pack(side='left', padx=(0, 5))
        ttk.Entry(row_b, textvariable=self.pdf_b).pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(row_b, text=_('Browser'), command=self._browse_b).pack(
            side='left', padx=(5, 0)
        )

        # Fixed two-row input: collapse to natural height, don't stretch the frame
        # (the base class defaults input_frame to expand=True, which suits list views
        # but leaves a large void here between the inputs and the output row).
        self.input_frame.pack_configure(expand=False, fill='x')

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output PDF'))
        self.output_path = tk.StringVar()
        ttk.Entry(self.output_frame, textvariable=self.output_path).pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(
            self.output_frame, text=_('Browser'), command=self._set_output_path
        ).pack(side='left', padx=(5, 0))

    def _setup_options_frame(self):
        self._reverse_b = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.options_frame, text=_('Reverse PDF B'), variable=self._reverse_b
        ).pack(side='left', padx=(5, 20))

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _browse_a(self):
        init = self._initial_dir(self.pdf_b.get() or self.pdf_a.get())
        path = askopenfilename(filetypes=FILE_TYPES['PDF'], initialdir=init)
        if path:
            self.pdf_a.set(Path(path))

    def _browse_b(self):
        init = self._initial_dir(self.pdf_a.get() or self.pdf_b.get())
        path = askopenfilename(filetypes=FILE_TYPES['PDF'], initialdir=init)
        if path:
            self.pdf_b.set(Path(path))

    @staticmethod
    def _initial_dir(current: str) -> Path | str:
        if current:
            return Path(current).parent
        return ''

    def _set_output_path(self):
        init_folder = ''
        init_file = ''
        current_input_path = self._get_current_input_path()
        if current_input_path:
            init_folder = current_input_path.parent
            init_file = current_input_path.with_suffix(f'.{_("Interleave")}.pdf').name
        output_path = asksaveasfilename(
            filetypes=FILE_TYPES['PDF'],
            defaultextension='pdf',
            initialdir=init_folder,
            initialfile=init_file,
            confirmoverwrite=True,
        )
        if output_path:
            self.output_path.set(Path(output_path))

    def _get_current_input_path(self):
        current = self.output_path.get()
        if current:
            return Path(current)
        for value in (self.pdf_a.get(), self.pdf_b.get()):
            if value:
                return Path(value)
        return None

    def get_input_paths(self):
        return [Path(self.pdf_a.get()), Path(self.pdf_b.get())]

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {
            'reverse_b': self._reverse_b.get(),
        }

    def _execute_handler(self):
        # Build params and run the interleave merge with a progress dialog.
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.interleave_merge.interleave_merge_worker import (
                run_interleave_with_progress,
            )

            run_interleave_with_progress(self.winfo_toplevel(), params)

    def _validate_input_files(self):
        if not self.pdf_a.get() or not self.pdf_b.get():
            showerror(title=_('Error'), message=_('Both input PDF must be specified.'))
            return False
        if not self.output_path.get():
            showerror(title=_('Error'), message=_('Output PDF must be specified.'))
            return False
        return True


if __name__ == '__main__':
    root = TkinterDnD.Tk()
    InterleaveMergeFrame(root).pack(fill='both', expand=True)
    root.mainloop()

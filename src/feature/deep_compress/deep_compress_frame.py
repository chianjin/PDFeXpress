import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno, showerror

from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.helpers import enable_pdf_drop
from util.i18n import gettext_text as _


class DeepCompressFrame(BaseFeatureFrame):
    """Deep compression: single-in -> single-out, re-encodes embedded images."""

    def __init__(self, master, **kw):
        super().__init__(master, feature_id='deep_compress', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))
        self.input_path = tk.StringVar()

        row = ttk.Frame(self.input_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self.input_path, state='readonly').pack(
            side='left', fill='x', expand=True
        )
        ttk.Button(row, text=_('Browser'), command=self._set_input_path).pack(
            side='left', padx=(5, 0)
        )

        # Fixed single-input: collapse to natural height.
        self.input_frame.pack_configure(expand=False, fill='x')
        enable_pdf_drop(self.input_frame, self.input_path)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output PDF'))
        self.output_path = tk.StringVar()

        row = ttk.Frame(self.output_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self.output_path, state='readonly').pack(
            side='left', fill='x', expand=True
        )
        ttk.Button(row, text=_('Browser'), command=self._set_output_path).pack(
            side='left', padx=(5, 0)
        )
        self.output_frame.pack_configure(expand=False, fill='x')

    def _setup_options_frame(self):
        ttk.Label(self.options_frame, text=_('Max Resolution')).pack(side='left')
        self._max_dpi = tk.IntVar(value=150)
        ttk.Entry(
            self.options_frame, textvariable=self._max_dpi, width=6, justify='center'
        ).pack(side='left', padx=(3, 0))
        ttk.Label(self.options_frame, text='dpi').pack(side='left', padx=(3, 0))

        ttk.Label(self.options_frame, text=_('JPG Quality')).pack(
            side='left', padx=(10, 0)
        )
        self._jpg_quality = tk.IntVar(value=75)
        ttk.Entry(
            self.options_frame,
            textvariable=self._jpg_quality,
            width=6,
            justify='center',
        ).pack(side='left', padx=(3, 0))

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
            self.output_path.set(Path(path).with_suffix(f'.{_('Compress')}.pdf'))

    def _set_output_path(self):
        output_path = self.output_path.get()
        init_folder = Path(output_path).parent if output_path else ''
        init_file = Path(output_path).name if output_path else ''
        path = asksaveasfilename(
            filetypes=FILE_TYPES['PDF'],
            defaultextension='.pdf',
            initialdir=init_folder,
            initialfile=init_file,
            confirmoverwrite=True,
        )
        if path:
            self.output_path.set(path)

    def get_input_paths(self):
        return [Path(self.input_path.get())] if self.input_path.get() else []

    def get_output_path(self):
        return Path(self.output_path.get()) if self.output_path.get() else None

    def get_options(self) -> dict:
        return {
            'max_dpi': self._max_dpi.get(),
            'jpg_quality': self._jpg_quality.get(),
        }

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if not self._validate_execute_params():
            return
        # Time-consuming operation: warn before running.
        ans = askyesno(
            title=_('Confirm'),
            message=_('Compressing embedded images is time-consuming. Continue?'),
        )
        if not ans:
            return
        from feature.deep_compress.deep_compress_worker import (
            run_deep_compress_with_progress,
        )

        run_deep_compress_with_progress(self.winfo_toplevel(), params)

    def _validate_execute_params(self):
        if not self.input_path.get():
            showerror(title=_('Error'), message=_('Input PDF must be set.'))
            return False
        if not Path(self.input_path.get()).is_file():
            showerror(title=_('Error'), message=_('Input PDF does not exist.'))
            return False
        if not self.output_path.get():
            showerror(title=_('Error'), message=_('Output PDF must be set.'))
            return False
        if self._max_dpi.get() <= 0:
            showerror(
                title=_('Error'),
                message=_('Max resolution must be greater than 0.'),
            )
            return False
        if self._jpg_quality.get() <= 0 or self._jpg_quality.get() > 100:
            showerror(
                title=_('Error'),
                message=_('JPG quality must be between 1 and 100.'),
            )
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    DeepCompressFrame(root).pack(fill='both', expand=True)
    root.mainloop()

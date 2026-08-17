import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror

from tkinterdnd2 import TkinterDnD

from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.helpers import enable_pdf_drop
from util.i18n import gettext_text as _


class PdfToLongImageFrame(BaseFeatureFrame):
    """Render selected PDF pages into a single long JPEG image.

    A single input PDF and a single output JPEG; internal DPI (150) and JPEG
    quality (80) are fixed. The page range is 1-based: a single page ``n``,
    an inclusive range ``n-m``, or empty for all pages.
    """

    def __init__(self, master, **kw):
        super().__init__(master, feature_id='pdf_to_long_image', **kw)

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

        # Single fixed-height input row: collapse the frame instead of letting
        # it stretch (base class defaults expand=True, which suits list views).
        self.input_frame.pack_configure(expand=False, fill='x')
        enable_pdf_drop(self.input_frame, self.input_path)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output Image'))
        self.output_path = tk.StringVar()
        ttk.Entry(
            self.output_frame, textvariable=self.output_path, state='readonly'
        ).pack(side='left', expand=True, fill='x')
        ttk.Button(
            self.output_frame, text=_('Browser'), command=self._set_output_path
        ).pack(side='left', padx=(5, 0))

    def _setup_options_frame(self):
        ttk.Label(self.options_frame, text=_('Page Range')).pack(
            side='left', padx=(0, 5)
        )
        self._range = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self._range, width=18).pack(
            side='left', fill='x', expand=True, padx=(0, 5)
        )
        ttk.Label(
            self.options_frame,
            text=_('1-Based, n Page / n-m Range / Empty = All'),
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
            self.output_path.set(Path(path).with_suffix('.jpg'))

    def _set_output_path(self):
        output_path = self.output_path.get()
        init_folder = Path(output_path).parent if output_path else ''
        init_file = Path(output_path).name if output_path else ''
        output_path = asksaveasfilename(
            filetypes=FILE_TYPES['JPEG'],
            defaultextension='jpg',
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
        if self.input_path.get():
            return Path(self.input_path.get())
        return None

    def get_input_paths(self):
        return [Path(self.input_path.get())] if self.input_path.get() else []

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {'range': self._range.get()}

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_execute_params():
            from feature.pdf_to_long_image.pdf_to_long_image_worker import (
                run_pdf_to_long_image_with_progress,
            )

            run_pdf_to_long_image_with_progress(self.winfo_toplevel(), params)

    def _validate_execute_params(self):
        if not self.input_path.get():
            showerror(
                title=_('Error'),
                message=_('Input PDF must be set.'),
            )
            return False
        if not self.output_path.get():
            showerror(
                title=_('Error'),
                message=_('Output path must be set.'),
            )
            return False
        return True


if __name__ == '__main__':
    root = TkinterDnD.Tk()
    PdfToLongImageFrame(root).pack(fill='both', expand=True)
    root.mainloop()

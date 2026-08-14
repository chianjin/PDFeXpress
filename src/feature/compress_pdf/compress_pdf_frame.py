import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesno, showerror

from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _
from widget import FileListView


class CompressPdfFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='compress_pdf', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('PDF List'))
        self.file_list_view = FileListView(self.input_frame, sortable=False)
        self.file_list_view.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
        self._compress_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.options_frame,
            text=_('Compress embedded images'),
            variable=self._compress_var,
        ).pack(side='left', padx=(0, 10))

        ttk.Label(self.options_frame, text=_('Max Resolution')).pack(side='left')
        self._max_dpi = tk.IntVar(value=150)
        ttk.Entry(self.options_frame, textvariable=self._max_dpi, width=6).pack(
            side='left', padx=(3, 0)
        )
        ttk.Label(self.options_frame, text='dpi').pack(side='left', padx=(3, 0))

        ttk.Label(self.options_frame, text=_('JPG Quality')).pack(
            side='left', padx=(10, 0)
        )
        self._jpg_quality = tk.IntVar(value=75)
        ttk.Entry(self.options_frame, textvariable=self._jpg_quality, width=6).pack(
            side='left', padx=(3, 0)
        )

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def get_input_paths(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {
            'compress_images': self._compress_var.get(),
            'max_dpi': self._max_dpi.get(),
            'jpg_quality': self._jpg_quality.get(),
        }

    def _set_output_folder(self):
        init_dir = self._get_initial_dir()
        folder = askdirectory(initialdir=init_dir)
        if folder:
            self.output_path.set(str(Path(folder)))

    def _get_initial_dir(self):
        current = self.output_path.get()
        if current:
            return Path(current)
        inputs = self.get_input_paths()
        if inputs:
            return inputs[0].parent
        return None

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if not self._validate_input_files():
            return
        # Time-consuming operation: warn before running.
        if params['options']['compress_images']:
            ans = askyesno(
                title=_('Confirm'),
                message=_('Compressing embedded images is time-consuming. Continue?'),
            )
            if not ans:
                return
        from feature.compress_pdf.compress_pdf_worker import (
            run_compress_pdf_with_progress,
        )

        run_compress_pdf_with_progress(self.winfo_toplevel(), params)

    def _validate_input_files(self):
        if len(self.get_input_paths()) < 1:
            showerror(
                title=_('Error'),
                message=_('Input must have at least 1 PDF file.'),
            )
            return False
        if not self.output_path.get():
            showerror(
                title=_('Error'),
                message=_('Output folder must be set.'),
            )
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
                message=_('jpg quality must be between 1 and 100.'),
            )
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    CompressPdfFrame(root).pack(fill='both', expand=True)
    root.mainloop()

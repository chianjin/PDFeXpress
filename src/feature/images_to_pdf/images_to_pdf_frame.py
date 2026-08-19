import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror

from tkinterdnd2 import TkinterDnD

from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.i18n import gettext_text as _
from widget import FileListView


class ImagesToPdfFrame(BaseFeatureFrame):
    """Convert a list of images into a single PDF.

    The image list is user-orderable (sortable=True) but the worker keeps the
    exact list order -- no automatic sorting is applied.
    """

    def __init__(self, master, **kw):
        super().__init__(master, feature_id='images_to_pdf', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Image List'))
        self.file_list_view = FileListView(self.input_frame, file_types=FILE_TYPES['IMAGES'], sortable=True)
        self.file_list_view.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output PDF'))
        self.output_path = tk.StringVar()
        ttk.Entry(self.output_frame, textvariable=self.output_path, state='readonly').pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(self.output_frame, text=_('Browser'), command=self._set_output_path).pack(
            side='left', padx=(5, 0)
        )

    def _setup_options_frame(self):
        # This feature has no options; hide the empty Options frame.
        self.options_frame.pack_forget()

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _set_output_path(self):
        init_folder = ''
        init_file = ''
        input_paths = self.get_input_paths()
        if input_paths:
            input_path = Path(input_paths[0])
            init_folder = Path(input_path).parent
            init_file = Path(input_path).with_suffix('.pdf')
        output_path = asksaveasfilename(
            filetypes=FILE_TYPES['PDF'],
            defaultextension='pdf',
            initialdir=init_folder,
            initialfile=init_file,
            confirmoverwrite=True,
        )
        if output_path:
            self.output_path.set(output_path)

    def get_input_paths(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {}

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_execute_params():
            from feature.images_to_pdf.images_to_pdf_worker import (
                run_images_to_pdf_with_progress,
            )

            run_images_to_pdf_with_progress(self.winfo_toplevel(), params)

    def _validate_execute_params(self):
        if len(self.get_input_paths()) < 1:
            showerror(
                title=_('Error'),
                message=_('Input must have at least 1 image file.'),
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
    ImagesToPdfFrame(root).pack(fill='both', expand=True)
    root.mainloop()

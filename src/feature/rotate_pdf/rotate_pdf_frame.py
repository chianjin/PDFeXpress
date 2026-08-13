import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from pathlib import Path

from widget import FileListView
from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _


# Radiobutton value = normalized rotation angle, clockwise positive
# (90 = clockwise 90, 270 = counter-clockwise 90, 180 = 180). This matches
# the PDF /Rotate convention, so the value is used directly as both the
# delta applied to page.rotation and the output filename suffix.

class RotatePdfFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='rotate_pdf', **kw)

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
        self._rotation = tk.IntVar(value=90)
        ttk.Radiobutton(
            self.options_frame, text='↻ 90°',
            variable=self._rotation, value=90,
        ).pack(side='left', padx=(5, 20))
        ttk.Radiobutton(
            self.options_frame, text='↺ 90°',
            variable=self._rotation, value=270,
        ).pack(side='left', padx=(5, 20))
        ttk.Radiobutton(
            self.options_frame, text=_('180°'),
            variable=self._rotation, value=180,
        ).pack(side='left', padx=(5, 20))

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame, text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def get_input_pathes(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def _set_output_folder(self):
        init_dir = self._get_initial_dir()
        folder = askdirectory(initialdir=init_dir)
        if folder:
            self.output_path.set(str(Path(folder)))

    def _get_initial_dir(self):
        # Mirror merge_pdf: anchor the dialog to the already-set output,
        # otherwise to the first input file's directory.
        current = self.output_path.get()
        if current:
            return Path(current)
        inputs = self.get_input_pathes()
        if inputs:
            return inputs[0].parent
        return None

    def get_options(self) -> dict:
        return {'delta': self._rotation.get()}

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_pathes(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.rotate_pdf.rotate_pdf_worker import run_rotate_with_progress
            run_rotate_with_progress(self.winfo_toplevel(), params)

    def _validate_input_files(self):
        if len(self.get_input_pathes()) < 1:
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
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    RotatePdfFrame(root).pack(fill='both', expand=True)
    root.mainloop()

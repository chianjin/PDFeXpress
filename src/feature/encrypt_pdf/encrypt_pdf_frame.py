import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror

from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _
from widget import FileListView


class EncryptPdfFrame(BaseFeatureFrame):
    """Encrypt multiple PDFs in a batch (AES-256, single shared password).

    Unordered multi-input mirrored from ``rotate_pdf``: results are written to
    a chosen output folder (defaulting to the first input's directory) as
    ``{stem}.{_('Encrypt')}.pdf``.
    """

    def __init__(self, master, **kw):
        super().__init__(master, feature_id='encrypt_pdf', **kw)

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
        ttk.Label(self.options_frame, text=_('Password')).pack(side='left', padx=(0, 5))
        self._password = tk.StringVar()
        # Local tool: no mask on the password field.
        ttk.Entry(self.options_frame, textvariable=self._password).pack(
            side='left', fill='x', expand=True
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

    def _set_output_folder(self):
        init_dir = self._get_initial_dir()
        folder = askdirectory(initialdir=init_dir)
        if folder:
            self.output_path.set(str(Path(folder)))

    def _get_initial_dir(self):
        # Anchor to the already-set output, else the first input's directory.
        current = self.output_path.get()
        if current:
            return Path(current)
        inputs = self.get_input_paths()
        if inputs:
            return inputs[0].parent
        return None

    def get_options(self) -> dict:
        return {'password': self._password.get()}

    def _execute_handler(self):
        # Default the output folder to the first input's directory when unset.
        if not self.output_path.get():
            inputs = self.get_input_paths()
            if inputs:
                self.output_path.set(str(inputs[0].parent))
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.encrypt_pdf.encrypt_pdf_worker import (
                run_encrypt_with_progress,
            )

            run_encrypt_with_progress(self.winfo_toplevel(), params)

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
        if not self._password.get():
            showerror(
                title=_('Error'),
                message=_('Password must not be empty.'),
            )
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    EncryptPdfFrame(root).pack(fill='both', expand=True)
    root.mainloop()

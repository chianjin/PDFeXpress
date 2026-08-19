import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror

from tkinterdnd2 import TkinterDnD

from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.i18n import gettext_text as _
from widget import FileListView


class MergeInvoicesFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='merge_invoices', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('PDF List'))
        self.file_list_view = FileListView(self.input_frame, sortable=False)
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
        self.options_frame.pack_forget()
        self.options_frame.destroy()

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _set_output_path(self):
        input_paths = self.get_input_paths()
        init_folder = input_paths[0].parent if input_paths else ''
        init_file = f'{_("MergedInvoice")}-{datetime.now().strftime("%Y%m%d")}.pdf'
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
        current_input_path = self.output_path.get()
        if current_input_path:
            return Path(current_input_path)
        current_input_paths = self.get_input_paths()
        if len(current_input_paths) > 0:
            return Path(current_input_paths[0])
        return None

    def get_input_paths(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {}

    def _execute_handler(self):
        # Build params and run the merge with a progress dialog.
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_execute_params():
            from feature.merge_invoices.merge_invoices_worker import (
                run_merge_invoices_with_progress,
            )

            run_merge_invoices_with_progress(self.winfo_toplevel(), params)

    def _validate_execute_params(self):
        current_input_paths = self.get_input_paths()
        if len(current_input_paths) < 2:
            showerror(title=_('Error'), message=_('Input must have at least 2 PDF files.'))
            return False
        if not self.output_path.get():
            showerror(title=_('Error'), message=_('Output path must be set.'))
            return False
        return True


if __name__ == '__main__':
    root = TkinterDnD.Tk()
    MergeInvoicesFrame(root).pack(fill='both', expand=True)
    root.mainloop()

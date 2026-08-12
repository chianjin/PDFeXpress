import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror
from pathlib import Path

from tkinterdnd2 import TkinterDnD

from widget import FileListView
from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _
from util.file_types import FILE_TYPES


class MergePdfFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='merge_pdf', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('PDF List'))
        self.file_list_view = FileListView(self.input_frame)
        self.file_list_view.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output PDF'))
        self.output_path = tk.StringVar()
        ttk.Entry(self.output_frame, textvariable=self.output_path).pack(side='left', expand=True, fill='x')
        ttk.Button(self.output_frame, text=_('Broswer'), command=self._set_output_path).pack(side='left', padx=(5, 0))

    def _setup_options_frame(self):
        self._generate_bookmarks = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.options_frame, text=_('Generate Bookmarks'), variable=self._generate_bookmarks
        ).pack(side='left', padx=(5, 20))
        self._support_delux_print = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.options_frame, text=_('Support Delux Printting'), variable=self._support_delux_print
        ).pack(side='left', padx=(5, 20))

    def _setup_execute_frame(self):
        self._execute_message = tk.StringVar(value=_('Ready.'))
        ttk.Label(self.execute_frame, textvariable=self._execute_message).pack(side='left', expand=True, fill='x')
        ttk.Button(
            self.execute_frame, text=_(self._executive_text), command=self._execute_handler
        ).pack(side='left', padx=(5, 0))

    def _set_output_path(self):
        init_folder = ''
        init_file = ''
        current_input_path = self._get_current_input_path()
        if current_input_path:
            init_folder = current_input_path.parent
            init_file = current_input_path.with_suffix(f'.{_('Merged')}.pdf').name
        output_path = asksaveasfilename(
            filetypes=FILE_TYPES['PDF'],
            defaultextension='pdf',
            initialdir=init_folder,
            initialfile=init_file,
            confirmoverwrite=True,
        )
        if output_path:
            self.output_path.set(str(Path(output_path)))

    def _get_current_input_path(self):
        current_input_path = self.output_path.get()
        if current_input_path:
            return Path(current_input_path)
        current_input_pathes = self.get_input_pathes()
        if len(current_input_pathes) > 0:
            return Path(current_input_pathes[0])
        return None

    def get_input_pathes(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {
            'generate_bookmarks': self._generate_bookmarks.get(),
            'support_delux_print': self._support_delux_print.get(),
        }

    def _validate_input_files(self):
        current_input_pathes = self.get_input_pathes()
        if len(current_input_pathes) < 2:
            showerror(
                title=_('Error'),
                message=_('Input must have at least 2 PDF files.')
            )
            return False
        if not self.output_path.get():
            showerror(
                title=_('Error'),
                message=_('Output path must be set.')
            )
            return False
        return True

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    MergePdfFrame(root).pack(fill='both', expand=True)
    root.mainloop()
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from pathlib import Path

from widget import FileListView
from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _


class ExtractImagesFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='extract_images', **kw)

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
        self._ignore_small = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.options_frame, text=_('Ignore small images'),
            variable=self._ignore_small,
        ).pack(side='left')

        ttk.Label(self.options_frame, text=_('Min Width')).pack(side='left', padx=(10, 0))
        self._min_w = tk.IntVar(value=50)
        ttk.Entry(self.options_frame, textvariable=self._min_w, width=6, justify='center').pack(
            side='left', padx=(3, 0)
        )
        ttk.Label(self.options_frame, text='x').pack(side='left', padx=(3, 0))
        ttk.Label(self.options_frame, text=_('Min Height')).pack(side='left')
        self._min_h = tk.IntVar(value=50)
        ttk.Entry(self.options_frame, textvariable=self._min_h, width=6, justify='center').pack(
            side='left', padx=(3, 0)
        )

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame, text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def get_input_pathes(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        w, h = self._get_min_dims()
        return {
            'ignore_small': self._ignore_small.get(),
            'min_w': w,
            'min_h': h,
        }

    def _get_min_dims(self):
        return int(self._min_w.get()), int(self._min_h.get())

    def _set_output_folder(self):
        init_dir = self._get_initial_dir()
        folder = askdirectory(initialdir=init_dir)
        if folder:
            self.output_path.set(str(Path(folder)))

    def _get_initial_dir(self):
        current = self.output_path.get()
        if current:
            return Path(current)
        inputs = self.get_input_pathes()
        if inputs:
            return inputs[0].parent
        return None

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_pathes(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.extract_images.extract_images_worker import run_extract_images_with_progress
            run_extract_images_with_progress(self.winfo_toplevel(), params)

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
        try:
            w, h = self._get_min_dims()
        except (ValueError, tk.TclError):
            showerror(
                title=_('Error'),
                message=_('Min width / min height must be integers.'),
            )
            return False
        if w < 0 or h < 0:
            showerror(
                title=_('Error'),
                message=_('Min width / min height must be non-negative.'),
            )
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    ExtractImagesFrame(root).pack(fill='both', expand=True)
    root.mainloop()

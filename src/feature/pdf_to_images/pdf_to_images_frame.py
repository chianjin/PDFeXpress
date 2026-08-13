import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from pathlib import Path

from tkinterdnd2 import TkinterDnD

from widget import FileListView
from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _
from util.file_types import FILE_TYPES


class PdfToImagesFrame(BaseFeatureFrame):
    """Render every page of each input PDF into image files.

    PNG keeps a transparent background when requested (alpha); JPEG ignores
    transparency and uses the quality setting instead.
    """

    def __init__(self, master, **kw):
        super().__init__(master, feature_id='pdf_to_images', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('PDF List'))
        self.file_list_view = FileListView(
            self.input_frame, file_types=FILE_TYPES['PDF'], sortable=False
        )
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
        ttk.Label(self.options_frame, text=_('Resolution')).pack(side='left')
        self._dpi = tk.IntVar(value=200)
        ttk.Entry(self.options_frame, textvariable=self._dpi, width=5, justify='center').pack(
            side='left', padx=(5, 0)
        )
        ttk.Label(self.options_frame, text=_('DPI')).pack(side='left')

        ttk.Label(self.options_frame, text=_('Format')).pack(side='left', padx=(10, 0))
        self._fmt = tk.StringVar(value='png')
        ttk.Radiobutton(
            self.options_frame, text='PNG', variable=self._fmt, value='png'
        ).pack(side='left', padx=(5, 0))
        self._transparent = tk.BooleanVar(value=True)
        self._transparent_cb = ttk.Checkbutton(
            self.options_frame, text=_('Transparent Background'),
            variable=self._transparent,
        )
        self._transparent_cb.pack(side='left', padx=(5, 0))
        ttk.Radiobutton(
            self.options_frame, text='JPG', variable=self._fmt, value='jpg'
        ).pack(side='left', padx=(10, 0))
        ttk.Label(self.options_frame, text=_('Quality')).pack(side='left', padx=(0, 3))
        self._quality = tk.IntVar(value=85)
        self._quality_entry = ttk.Entry(
            self.options_frame, textvariable=self._quality, width=6
        )
        self._quality_entry.pack(side='left', padx=(5, 0))

        self._fmt.trace_add('write', self._on_fmt_change)
        self._on_fmt_change()

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame, text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _on_fmt_change(self, *args):
        png = self._fmt.get() == 'png'
        self._transparent_cb.configure(state='normal' if png else 'disabled')
        self._quality_entry.configure(state='disabled' if png else 'normal')

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

    def get_input_pathes(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {
            'dpi': self._dpi.get(),
            'fmt': self._fmt.get(),
            'transparent': self._transparent.get(),
            'quality': self._quality.get(),
        }

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_pathes(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.pdf_to_images.pdf_to_images_worker import (
                run_pdf_to_images_with_progress,
            )
            run_pdf_to_images_with_progress(self.winfo_toplevel(), params)

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
            dpi = int(self._dpi.get())
        except (ValueError, tk.TclError):
            showerror(title=_('Error'), message=_('DPI must be an integer.'))
            return False
        if dpi < 1:
            showerror(title=_('Error'), message=_('DPI must be >= 1.'))
            return False
        try:
            quality = int(self._quality.get())
        except (ValueError, tk.TclError):
            showerror(title=_('Error'), message=_('Quality must be an integer.'))
            return False
        if quality < 1 or quality > 100:
            showerror(title=_('Error'), message=_('Quality must be between 1 and 100.'))
            return False
        return True


if __name__ == '__main__':
    root = TkinterDnD.Tk()
    PdfToImagesFrame(root).pack(fill='both', expand=True)
    root.mainloop()
